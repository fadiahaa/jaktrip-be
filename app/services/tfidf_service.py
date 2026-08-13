import re

from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.utils.stopwords import STOPWORDS_ID


class TFIDFService:

    # Membuat stemmer Bahasa Indonesia
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()

    @staticmethod
    def preprocess(text: str) -> str:
        """
        Preprocessing teks Bahasa Indonesia:
        1. Case folding
        2. Membersihkan karakter selain huruf
        3. Tokenisasi
        4. Stopword removal
        5. Stemming
        """

        if not text:
            return ""

        # 1. Case folding
        text = text.lower()

        # 2. Hilangkan URL
        text = re.sub(r"http\S+|www\S+", " ", text)

        # 3. Hilangkan angka dan karakter khusus
        text = re.sub(r"[^a-zA-Z\s]", " ", text)

        # 4. Rapikan spasi
        text = re.sub(r"\s+", " ", text).strip()

        # 5. Tokenisasi sederhana
        tokens = text.split()

        # 6. Stopword removal
        tokens = [
            word
            for word in tokens
            if word not in STOPWORDS_ID
        ]

        # 7. Stemming Bahasa Indonesia
        text = " ".join(tokens)

        text = TFIDFService.stemmer.stem(text)

        return text

    @staticmethod
    def recommend(preferensi: str, wisata_list):

        # ==========================================
        # 1. PREPROCESSING PREFERENSI USER
        # ==========================================

        query = TFIDFService.preprocess(
            preferensi
        )

        # ==========================================
        # 2. PREPROCESSING DESKRIPSI WISATA
        # ==========================================

        documents = [
            TFIDFService.preprocess(
                wisata.deskripsi or ""
            )
            for wisata in wisata_list
        ]

        # ==========================================
        # 3. GABUNGKAN DOKUMEN + QUERY
        # ==========================================

        documents.append(query)

        # ==========================================
        # 4. TF-IDF
        # ==========================================

        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words=STOPWORDS_ID
        )

        tfidf_matrix = vectorizer.fit_transform(
            documents
        )

        # ==========================================
        # 5. PISAHKAN QUERY DAN DOKUMEN
        # ==========================================

        query_vector = tfidf_matrix[-1]

        wisata_vectors = tfidf_matrix[:-1]

        # ==========================================
        # 6. COSINE SIMILARITY
        # ==========================================

        similarities = cosine_similarity(
            query_vector,
            wisata_vectors
        ).flatten()

        # ==========================================
        # 7. BENTUK HASIL
        # ==========================================

        hasil = []

        for wisata, score in zip(
            wisata_list,
            similarities
        ):

            hasil.append({
                "id_wisata": wisata.id_wisata,
                "nama_wisata": wisata.nama_wisata,
                "kategori": wisata.kategori,
                "harga_min": float(
                    wisata.harga_min
                ),
                "harga_max": float(
                    wisata.harga_max
                ),
                "estimasi_durasi": wisata.estimasi_durasi,
                "latitude": float(
                    wisata.latitude
                ),
                "longitude": float(
                    wisata.longitude
                ),
                "similarity": float(score)
            })

        # ==========================================
        # 8. RANKING
        # ==========================================

        hasil.sort(
            key=lambda x: x["similarity"],
            reverse=True
        )

        return hasil