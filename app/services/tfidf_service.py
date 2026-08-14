import re

from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.utils.stopwords import STOPWORDS_ID


class TFIDFService:
    SYNONYMS = {
        "hewan": "satwa",
        "binatang": "satwa",
        "fauna": "satwa",
        "pohon": "pepohonan",
        "makanan": "kuliner",
        "makan": "kuliner"
    }
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

        # 6. Normalisasi sinonim
        tokens = [
            TFIDFService.SYNONYMS.get(word, word)
            for word in tokens
        ]

        # 7. Stopword removal
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

        # Catatan: nama_wisata sengaja TIDAK dimasukkan ke teks TF-IDF.
        # Nama tempat adalah proper noun yang hampir selalu unik per
        # dokumen, sehingga hanya menambah dimensi kata yang tidak
        # relevan dengan preferensi user dan mengencerkan (dilute)
        # nilai cosine similarity secara keseluruhan.
        #
        # kategori diulang 3x supaya diberi bobot lebih tinggi,
        # karena kategori adalah sinyal paling kuat untuk mencocokkan
        # preferensi user (mis. "alam", "kuliner", "sejarah").
        documents = [
            TFIDFService.preprocess(
                f"{(wisata.kategori + ' ') * 3}"
                f"{wisata.deskripsi or ''}"
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

        # sublinear_tf=True: pakai skala 1 + log(tf) alih-alih tf linear.
        # Ini mengurangi dominasi kata yang berulang dan membuat skor
        # similarity lebih representatif untuk dokumen pendek seperti
        # deskripsi wisata.
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words=STOPWORDS_ID,
            sublinear_tf=True,
            smooth_idf=True
        )

        tfidf_matrix = vectorizer.fit_transform(
            documents
        )
        features = vectorizer.get_feature_names_out()

        query_values = tfidf_matrix[-1].toarray().flatten()

        print("\n========== HASIL TF-IDF QUERY ==========")

        for term, value in zip(features, query_values):
            if value > 0:
                print(f"{term}: {value:.4f}")

        print("=========================================\n")
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
            if score < 0.02:
                    continue

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
            
        if not hasil:
            return []

        # ==========================================
        # 8. RANKING
        # ==========================================

        hasil.sort(
            key=lambda x: x["similarity"],
            reverse=True
        )

        return hasil