import os

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from database import get_connection
from pydantic import BaseModel
from recommender import get_recommendations
from fastapi.staticfiles import StaticFiles
from auth import (
    hash_password,
    verify_password,
    create_access_token
)
from fastapi import Depends
from auth import get_current_user
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
# =========================
# FASTAPI
# =========================

app = FastAPI(
    title="Wisata Jakarta Recommendation API"
)
configured_cors_origins = os.getenv("CORS_ORIGINS", "")
allow_origins = [
    origin.strip().rstrip("/")
    for origin in configured_cors_origins.split(",")
    if origin.strip()
]
if not allow_origins:
    allow_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount(
    "/images",
    StaticFiles(directory="static/images"),
    name="images"
)

# =========================
# REQUEST MODEL
# =========================

class RecommendationRequest(BaseModel):
    query: str


# =========================
# ROOT
# =========================

@app.get("/")
def root():
    return {
        "message": "Wisata Jakarta API berjalan!"
    }


# =========================
# TEST DATABASE
# =========================

@app.get("/test-db")
def test_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM destinations"
    )

    jumlah = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return {
        "status": "success",
        "jumlah_destinasi": jumlah
    }


# =========================
# GET ALL DESTINATIONS
# =========================

@app.get("/destinations")
def get_destinations():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            place_name,
            description,
            category,
            city,
            price,
            rating,
            image
        FROM destinations
        ORDER BY id ASC
    """)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    destinations = []

    for row in rows:
        destinations.append({
            "id": row[0],
            "place_name": row[1],
            "description": row[2],
            "category": row[3],
            "city": row[4],
            "price": row[5],
            "rating": float(row[6])
                if row[6] is not None
                else None,
            "image": f"/images/{row[7]}"
        })

    return destinations

@app.get("/destinations/{destination_id}")
def get_destination_detail(destination_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            place_name,
            description,
            category,
            city,
            price,
            rating,
            image
        FROM destinations
        WHERE id = %s
    """, (destination_id,))

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Destinasi tidak ditemukan"
        )

    destination = {
        "id": row[0],
        "place_name": row[1],
        "description": row[2],
        "category": row[3],
        "city": row[4],
        "price": row[5],
        "rating": float(row[6])
            if row[6] is not None
            else None,
        "image": f"/images/{row[7]}"
    }

    return {
        "status": "success",
        "destination": destination
    }
# =========================
# RECOMMENDATION
# =========================

@app.post("/recommend")
def recommend(request: RecommendationRequest):

    recommendations = get_recommendations(
        request.query,
        top_n=5
    )


    # =========================
    # JIKA QUERY TIDAK VALID
    # =========================

    if recommendations["status"] != "success":
        return {
            "query": request.query,
            "status": recommendations["status"],
            "message": recommendations["message"],
            "recommendations": []
        }


    # =========================
    # AMBIL DATA DARI DATABASE
    # =========================

    conn = get_connection()
    cursor = conn.cursor()

    results = []


    for item in recommendations["results"]:

        cursor.execute("""
            SELECT
                id,
                place_name,
                description,
                category,
                city,
                price,
                rating,
                image
            FROM destinations
            WHERE id = %s
        """, (
            item["index"] + 1,
        ))

        row = cursor.fetchone()


        if row:

            results.append({
                "id": row[0],
                "place_name": row[1],
                "description": row[2],
                "category": row[3],
                "city": row[4],
                "price": row[5],
                "rating": float(row[6])
                    if row[6] is not None
                    else None,
                "image": (
                    f"/images/{row[7]}"
                    if row[7]
                    else None
                ),
                "similarity": item["similarity"]
            })


    cursor.close()
    conn.close()


    return {
        "query": request.query,
        "status": "success",
        "recommendations": results
    }

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/register")
def register(request: RegisterRequest):

    conn = get_connection()
    cursor = conn.cursor()

    # Cek email sudah terdaftar
    cursor.execute("""
        SELECT id
        FROM users
        WHERE email = %s
    """, (request.email,))

    existing_user = cursor.fetchone()

    if existing_user:
        cursor.close()
        conn.close()

        return {
            "status": "error",
            "message": "Email sudah terdaftar"
        }

    # Hash password
    password_hash = hash_password(
        request.password
    )

    # Simpan user
    cursor.execute("""
        INSERT INTO users
        (username, email, password_hash)
        VALUES (%s, %s, %s)
        RETURNING id
    """, (
        request.username,
        request.email,
        password_hash
    ))

    user_id = cursor.fetchone()[0]

    conn.commit()

    cursor.close()
    conn.close()

    return {
        "status": "success",
        "message": "Registrasi berhasil",
        "user_id": user_id
    }
    
@app.post("/login")
def login(request: LoginRequest):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            username,
            email,
            password_hash
        FROM users
        WHERE email = %s
    """, (request.email,))

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    # Email tidak ditemukan
    if not user:
        return {
            "status": "error",
            "message": "Email atau password salah"
        }

    user_id = user[0]
    username = user[1]
    email = user[2]
    password_hash = user[3]

    # Cek password
    if not verify_password(
        request.password,
        password_hash
    ):
        return {
            "status": "error",
            "message": "Email atau password salah"
        }

    # Buat JWT
    token = create_access_token(
        user_id
    )

    return {
        "status": "success",
        "message": "Login berhasil",
        "access_token": token,
        "user": {
            "id": user_id,
            "username": username,
            "email": email
        }
    }

@app.get("/me")
def get_me(
    user_id: int = Depends(get_current_user)
):
    return {
        "status": "success",
        "user_id": user_id
    }

class FavoriteRequest(BaseModel):
    destination_id: int
    
@app.post("/favorites")
def add_favorite(
    request: FavoriteRequest,
    user_id: int = Depends(get_current_user)
):

    conn = get_connection()
    cursor = conn.cursor()

    # Cek destinasi
    cursor.execute("""
        SELECT id
        FROM destinations
        WHERE id = %s
    """, (request.destination_id,))

    destination = cursor.fetchone()

    if not destination:
        cursor.close()
        conn.close()

        return {
            "status": "error",
            "message": "Destinasi tidak ditemukan"
        }

    # Cek sudah disimpan atau belum
    cursor.execute("""
        SELECT id
        FROM favorites
        WHERE user_id = %s
        AND destination_id = %s
    """, (
        user_id,
        request.destination_id
    ))

    existing = cursor.fetchone()

    if existing:
        cursor.close()
        conn.close()

        return {
            "status": "error",
            "message": "Destinasi sudah disimpan"
        }

    # Simpan
    cursor.execute("""
        INSERT INTO favorites
        (user_id, destination_id)
        VALUES (%s, %s)
        RETURNING id
    """, (
        user_id,
        request.destination_id
    ))

    favorite_id = cursor.fetchone()[0]

    conn.commit()

    cursor.close()
    conn.close()

    return {
        "status": "success",
        "message": "Destinasi berhasil disimpan",
        "favorite_id": favorite_id
    }

@app.get("/favorites")
def get_favorites(
    user_id: int = Depends(get_current_user)
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            d.id,
            d.place_name,
            d.description,
            d.category,
            d.city,
            d.price,
            d.rating,
            d.image
        FROM favorites f
        JOIN destinations d
            ON f.destination_id = d.id
        WHERE f.user_id = %s
        ORDER BY f.id DESC
    """, (user_id,))

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    results = []

    for row in rows:
        results.append({
            "id": row[0],
            "place_name": row[1],
            "description": row[2],
            "category": row[3],
            "city": row[4],
            "price": row[5],
            "rating": float(row[6])
                if row[6] is not None
                else None,
            "image": row[7]
        })

    return {
        "status": "success",
        "favorites": results
    }

@app.delete("/favorites/{destination_id}")
def delete_favorite(
    destination_id: int,
    user_id: int = Depends(get_current_user)
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM favorites
        WHERE user_id = %s
        AND destination_id = %s
        RETURNING id
    """, (
        user_id,
        destination_id
    ))

    deleted = cursor.fetchone()

    if not deleted:
        cursor.close()
        conn.close()

        return {
            "status": "error",
            "message": "Destinasi tidak ditemukan di daftar simpanan"
        }

    conn.commit()

    cursor.close()
    conn.close()

    return {
        "status": "success",
        "message": "Destinasi berhasil dihapus"
    }