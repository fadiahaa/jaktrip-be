import re
import joblib

from Sastrawi.StopWordRemover.StopWordRemoverFactory import (
    StopWordRemoverFactory
)
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from sklearn.metrics.pairwise import cosine_similarity


# =========================
# LOAD MODEL
# =========================

vectorizer = joblib.load(
    "model/tfidf_vectorizer.pkl"
)

tfidf_matrix = joblib.load(
    "model/tfidf_matrix.pkl"
)


# =========================
# STOPWORD
# =========================

stopword_factory = StopWordRemoverFactory()

stopwords = set(
    stopword_factory.get_stop_words()
)


# =========================
# STEMMER
# =========================

stemmer_factory = StemmerFactory()
stemmer = stemmer_factory.create_stemmer()


# =========================
# CLEANING
# =========================

def clean_text(text):
    text = str(text).lower()

    text = re.sub(
        r"[^a-zA-Z\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


# =========================
# STOPWORD REMOVAL
# =========================

def remove_stopwords(text):
    words = text.split()

    words = [
        word
        for word in words
        if word not in stopwords
    ]

    return " ".join(words)


# =========================
# PREPROCESSING
# =========================

def preprocess_text(text):
    text = clean_text(text)
    text = remove_stopwords(text)
    text = stemmer.stem(text)

    return text
 
def get_recommendations(query, top_n=5):

    # =========================
    # VALIDASI INPUT
    # =========================

    if not query or not query.strip():
        return {
            "status": "invalid",
            "message": "Silakan masukkan preferensi wisata."
        }


    # =========================
    # PREPROCESSING QUERY
    # =========================

    query_clean = preprocess_text(query)


    # Jika setelah preprocessing tidak ada kata
    if not query_clean.strip():
        return {
            "status": "invalid",
            "message": (
                "Preferensi belum cukup jelas. "
                "Coba masukkan jenis wisata yang kamu inginkan."
            )
        }


    # =========================
    # TF-IDF QUERY
    # =========================

    query_vector = vectorizer.transform(
        [query_clean]
    )


    # =========================
    # CEK KATA YANG DIKENALI
    # =========================

    if query_vector.nnz == 0:
        return {
            "status": "not_found",
            "message": (
                "Maaf, preferensi tersebut belum "
                "dapat digunakan untuk rekomendasi wisata."
            )
        }


    # =========================
    # COSINE SIMILARITY
    # =========================

    similarity_scores = cosine_similarity(
        query_vector,
        tfidf_matrix
    ).flatten()


    # =========================
    # RANKING
    # =========================

    top_indices = similarity_scores.argsort()[::-1]

    # Ambil kandidat yang similarity > 0
    valid_indices = [
        index
        for index in top_indices
        if similarity_scores[index] > 0
    ]


    # Tidak ada destinasi yang cocok
    if len(valid_indices) == 0:
        return {
            "status": "not_found",
            "message": (
                "Maaf, belum ditemukan destinasi "
                "yang sesuai dengan preferensimu."
            )
        }


    # Ambil Top N
    valid_indices = valid_indices[:top_n]


    results = []

    for index in valid_indices:

        results.append({
            "index": int(index),
            "similarity": float(
                similarity_scores[index]
            )
        })


    return {
        "status": "success",
        "results": results
    }