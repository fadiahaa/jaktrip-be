import json
from app.repositories.wisata_repository import WisataRepository
from google import genai
from types import SimpleNamespace

from app.core.config import GEMINI_API_KEY
from app.services.recommendation_service import RecommendationService


client = genai.Client(
    api_key=GEMINI_API_KEY
)


class ChatService:
    @staticmethod
    def call_gemini(prompt: str):

        models = [
            "gemini-3.6-flash",
            "gemini-3.5-flash",
            "gemini-2.5-flash"
        ]

        last_error = None

        for model in models:

            try:

                print(f"Mencoba model: {model}")

                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )

                print(f"Berhasil memakai {model}")

                return response.text

            except Exception as e:

                print(f"Model {model} gagal:")
                print(e)

                last_error = e

        raise last_error
    
    @staticmethod
    def is_list_question(message):

        text = message.lower().strip()

        keywords = [
            "wisata apa saja",
            "wisata apa aja",
            "ada wisata apa",
            "ada tempat wisata apa",
            "tempat wisata apa saja",
            "tempat wisata apa aja",
            "sebutkan wisata",
            "daftar wisata",
            "wisata yang ada",
            "tempat wisata yang ada"
        ]

        return any(
            keyword in text
            for keyword in keywords
        )
    
    @staticmethod
    def detect_intent(message: str):

        prompt = f"""
    Kamu adalah sistem untuk menentukan maksud pesan pengguna
    pada aplikasi wisata Jakarta bernama JakTrip.

    Pilih SATU intent:

    1. "greeting"
    Untuk sapaan seperti:
    - Halo
    - Hai
    - Selamat pagi

    2. "list"
    Untuk pengguna yang meminta daftar wisata.
    Contoh:
    - Wisata apa saja di Jakarta?
    - Sebutkan wisata di Jakarta
    - Ada tempat wisata apa?
    - Wisata sejarah di Jakarta ada apa saja?

    3. "information"
    Untuk pengguna yang meminta informasi tentang destinasi tertentu.
    Contoh:
    - Berikan informasi tentang Dufan
    - Dufan itu apa?
    - Berapa harga Dufan?
    - Ceritakan tentang Taman Suropati

    4. "recommendation"
    Untuk pengguna yang meminta rekomendasi atau menjelaskan
    keinginan perjalanan.
    Contoh:
    - Aku mau jalan-jalan santai
    - Cari tempat yang bagus untuk foto
    - Aku ingin wisata sejarah
    - Rekomendasikan tempat untuk liburan

    PENTING:
    Jika pengguna meminta daftar wisata, gunakan "list".
    Jika pengguna meminta informasi tentang satu destinasi tertentu,
    gunakan "information".
    Jika pengguna meminta atau membutuhkan rekomendasi perjalanan,
    gunakan "recommendation".

    Jawab HANYA JSON:

    {{
        "intent": "list",
        "wisata": ""
    }}

    Jika intent adalah information, isi "wisata" dengan nama destinasi.

    Pesan pengguna:
    {message}
    """

        response = ChatService.call_gemini(prompt)

        try:
            text = response.strip()

            if text.startswith("```json"):
                text = text[7:]

            if text.startswith("```"):
                text = text[3:]

            if text.endswith("```"):
                text = text[:-3]

            data = json.loads(text.strip())

            intent = data.get(
                "intent",
                "recommendation"
            )

            if intent not in [
                "greeting",
                "list",
                "information",
                "recommendation"
            ]:
                intent = "recommendation"

            return {
                "intent": intent,
                "wisata": data.get("wisata", "")
            }

        except Exception as e:

            print("Gagal mendeteksi intent:", e)

            return {
                "intent": "recommendation",
                "wisata": ""
            }
    
    @staticmethod
    def find_wisata(db, query):

        wisata_list = WisataRepository.get_all(db)

        query = query.lower().strip()

        for wisata in wisata_list:

            nama = wisata.nama_wisata.lower()

            if query in nama or nama in query:
                return wisata

        return None
    
    @staticmethod
    def generate_information_reply(message, wisata):

        harga_min = int(wisata.harga_min)
        harga_max = int(wisata.harga_max)

        prompt = f"""
    Kamu adalah JakTrip AI, asisten informasi wisata Jakarta.

    Jawab pertanyaan pengguna berdasarkan DATA DESTINASI
    yang diberikan.

    DATA DESTINASI:

    Nama: {wisata.nama_wisata}
    Kategori: {wisata.kategori}
    Deskripsi: {wisata.deskripsi or "Tidak tersedia"}
    Harga minimum: Rp{harga_min:,}
    Harga maksimum: Rp{harga_max:,}
    Estimasi durasi: {wisata.estimasi_durasi} menit

    Pertanyaan:
    {message}

    ATURAN:
    - Gunakan hanya data di atas.
    - Jangan mengarang informasi.
    - Jangan menyebut database atau algoritma.
    - Jika informasi tidak tersedia, katakan bahwa informasi tersebut
    belum tersedia.
    - Jangan merekomendasikan destinasi lain.
    - Jangan menyapa pengguna.
    - Gunakan bahasa Indonesia yang natural.
    - Maksimal 100 kata.
    """

        return ChatService.call_gemini(
            prompt
        ).strip()
    
    @staticmethod
    def generate_list_reply(db):

        wisata_list = WisataRepository.get_all(db)

        if not wisata_list:
            return {
                "reply": "Maaf, belum ada data destinasi wisata yang tersedia.",
                "destinations": []
            }

        grouped = {}

        for wisata in wisata_list:

            kategori = wisata.kategori or "Lainnya"

            if kategori not in grouped:
                grouped[kategori] = []

            grouped[kategori].append(
                wisata.nama_wisata
            )

        reply = ChatService.format_list_reply(
            grouped
        )

        destinations = [
            {
                "id_wisata": wisata.id_wisata,
                "nama_wisata": wisata.nama_wisata,
                "kategori": wisata.kategori
            }
            for wisata in wisata_list
        ]

        return {
            "reply": reply,
            "destinations": destinations
        }
    
    @staticmethod
    def format_list_reply(grouped):

        lines = [
            "Tentu! Berikut beberapa destinasi wisata "
            "yang tersedia di Jakarta:"
        ]

        for kategori, names in grouped.items():

            lines.append(f"\n{kategori}:")

            for name in names[:5]:
                lines.append(f"- {name}")

            if len(names) > 5:
                lines.append(
                    f"- dan {len(names) - 5} destinasi lainnya"
                )

        lines.append(
            "\nKamu juga bisa menanyakan informasi "
            "tentang destinasi tertentu."
        )

        return "\n".join(lines)
    
    @staticmethod
    def extract_preference(message: str):

        prompt = f"""
    Kamu adalah asisten JakTrip.

    Tugasmu adalah mengambil PREFERENSI WISATA dari kalimat pengguna.

    Pertahankan preferensi dalam bentuk kalimat atau frasa yang lengkap.
    JANGAN mengubahnya menjadi satu kategori saja seperti:
    - alam
    - sejarah
    - kuliner
    - budaya
    - hiburan

    Jika pengguna menyebut beberapa aktivitas atau keinginan,
    pertahankan semuanya.

    Contoh:

    Input:
    Saya ingin makan makanan khas Jakarta, kemudian jalan-jalan santai
    dan mencari tempat yang bagus untuk foto.

    Output:
    {{"preferensi":"makan makanan khas Jakarta, jalan-jalan santai, dan mencari tempat yang bagus untuk foto"}}

    Input:
    Saya ingin mengunjungi museum dan tempat bersejarah untuk belajar
    tentang sejarah Jakarta.

    Output:
    {{"preferensi":"mengunjungi museum dan tempat bersejarah untuk belajar tentang sejarah Jakarta"}}

    Input:
    Saya ingin tempat yang tenang, banyak pohon, dan cocok untuk bersantai.

    Output:
    {{"preferensi":"tempat yang tenang, banyak pohon, dan cocok untuk bersantai"}}

    Jawab HANYA JSON valid.

    Kalimat pengguna:
    {message}
    """

        response = ChatService.call_gemini(prompt)

        try:
            text = response.strip()

            # Bersihkan markdown code block jika Gemini memberikannya
            if text.startswith("```json"):
                text = text[7:]

            if text.startswith("```"):
                text = text[3:]

            if text.endswith("```"):
                text = text[:-3]

            text = text.strip()

            data = json.loads(text)

            preferensi = data.get("preferensi")

            if preferensi:
                return preferensi.strip()

        except Exception as e:
            print("Gagal extract preference:", e)

        # fallback
        return message
    
    @staticmethod
    def generate_reply(message, preferensi, recommendation):

        places = ""

        for index, item in enumerate(
            recommendation["itinerary"],
            start=1
        ):
            places += f"""
    {index}. {item["nama_wisata"]}
    Kategori: {item["kategori"]}
    Harga minimum: Rp{int(item["harga_min"]):,}
    Harga maksimum: Rp{int(item["harga_max"]):,}
    Estimasi durasi: {item["estimasi_durasi"]} menit
    """

        summary = recommendation["summary"]

        prompt = f"""
    Kamu adalah JakTrip AI, asisten perjalanan wisata Jakarta.

    Tugasmu adalah menjelaskan hasil rekomendasi yang diberikan
    oleh sistem kepada pengguna.

    ATURAN WAJIB:

    1. HANYA gunakan informasi yang terdapat pada data destinasi
    dan summary di bawah.
    2. Jangan mengarang informasi tentang destinasi.
    3. Jangan menyebutkan fasilitas, suasana, spot foto, makanan,
    aktivitas, atau informasi lain yang tidak tersedia pada data.
    4. Jangan membuat rekomendasi destinasi baru.
    5. Jangan mengubah harga, jumlah destinasi, durasi, atau jarak.
    6. Jangan menyebut TF-IDF, cosine similarity, algoritma,
    database, atau proses internal sistem.
    7. Jangan memperkenalkan diri.
    8. Jangan menggunakan kata "Halo", "Hai", atau "Selamat datang".
    9. Gunakan bahasa Indonesia yang natural, ramah, dan singkat.
    10. Sebutkan nama destinasi yang direkomendasikan.
    11. Sebutkan total biaya dan total jarak.
    12. Maksimal 100 kata.

    Preferensi pengguna:
    {preferensi}

    Summary:
    Jumlah destinasi: {summary["jumlah_destinasi"]}
    Total biaya: Rp{int(summary["total_biaya"]):,}
    Total durasi: {summary["total_durasi"]} menit
    Total jarak: {summary["total_jarak_km"]} km

    Data destinasi:
    {places}

    Pesan pengguna:
    {message}
    """

        reply = ChatService.call_gemini(prompt)

        # Bersihkan sapaan jika Gemini masih menggunakannya
        reply = reply.strip()

        if reply.lower().startswith("halo!"):
            reply = reply[5:].strip()

        elif reply.lower().startswith("halo"):
            reply = reply[4:].strip()

        return reply
    
    @staticmethod
    def chat(db, request):

        message = request.message.strip()

        if not message:
            return {
                "reply": (
                    "Silakan tuliskan pertanyaan atau "
                    "rencana perjalananmu."
                )
            }

        # ==========================================
        # LIST DESTINASI
        # ==========================================

        if ChatService.is_list_question(message):

            result = ChatService.generate_list_reply(db)

            return {
                "intent": "list",
                "reply": result["reply"],
                "destinations": result["destinations"]
            }

        # ==========================================
        # DETEKSI INTENT
        # ==========================================

        intent_data = ChatService.detect_intent(message)

        intent = intent_data["intent"]
        wisata_query = intent_data["wisata"]

        print("Intent:", intent)
        print("Wisata:", wisata_query)

        # ==========================================
        # GREETING
        # ==========================================

        if intent == "greeting":

            reply = ChatService.call_gemini("""
    Kamu adalah JakTrip AI, asisten perjalanan wisata Jakarta.

    Perkenalkan dirimu secara singkat dan tanyakan
    perjalanan seperti apa yang ingin dilakukan pengguna.

    Gunakan bahasa Indonesia yang ramah dan natural.
    Maksimal 40 kata.
    """)

            return {
                "intent": "greeting",
                "reply": reply.strip()
            }

        # ==========================================
        # INFORMATION
        # ==========================================

        if intent == "information":

            if not wisata_query:

                return {
                    "intent": "information",
                    "reply": (
                        "Destinasi apa yang ingin kamu ketahui? "
                        "Contohnya Dufan atau Taman Suropati."
                    )
                }

            wisata = ChatService.find_wisata(
                db,
                wisata_query
            )

            if not wisata:

                return {
                    "intent": "information",
                    "reply": (
                        f"Maaf, saya belum menemukan destinasi "
                        f"'{wisata_query}' di dalam data wisata."
                    )
                }

            reply = ChatService.generate_information_reply(
                message,
                wisata
            )

            return {
                "intent": "information",
                "wisata": {
                    "id_wisata": wisata.id_wisata,
                    "nama_wisata": wisata.nama_wisata,
                    "kategori": wisata.kategori,
                    "harga_min": float(wisata.harga_min),
                    "harga_max": float(wisata.harga_max),
                    "estimasi_durasi": wisata.estimasi_durasi
                },
                "reply": reply
            }

        # ==========================================
        # RECOMMENDATION
        # ==========================================

        preferensi = ChatService.extract_preference(
            message
        )

        # ==========================================
        # NORMALISASI LOKASI
        # ==========================================

        latitude = request.latitude
        longitude = request.longitude

        if latitude == 0 and longitude == 0:

            latitude = None
            longitude = None

        # ==========================================
        # REQUEST RECOMMENDATION
        # ==========================================

        recommendation_request = SimpleNamespace(

            preferensi=preferensi,

            budget=request.budget,

            jumlah_orang=request.jumlah_orang,

            jumlah_destinasi=request.jumlah_destinasi,

            latitude=latitude,

            longitude=longitude
        )

        recommendation = RecommendationService.generate(
            db,
            recommendation_request
        )

        # ==========================================
        # TIDAK ADA HASIL
        # ==========================================

        if not recommendation["itinerary"]:

            return {

                "intent": "recommendation",

                "preferensi": preferensi,

                "reply": (
                    "Maaf, saya belum menemukan destinasi "
                    "yang sesuai dengan preferensi dan budget tersebut. "
                    "Coba gunakan budget yang lebih besar atau "
                    "jelaskan preferensi perjalanan yang berbeda."
                ),

                "summary": recommendation["summary"],

                "recommendations": []
            }

        # ==========================================
        # GENERATE REPLY
        # ==========================================

        reply = ChatService.generate_reply(
            message,
            preferensi,
            recommendation
        )

        return {

            "intent": "recommendation",

            "preferensi": preferensi,

            "reply": reply,

            "summary": recommendation["summary"],

            "recommendations": recommendation["itinerary"]
        }