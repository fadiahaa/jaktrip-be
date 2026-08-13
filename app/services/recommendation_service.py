from app.repositories.wisata_repository import WisataRepository
from app.services.tfidf_service import TFIDFService
from app.services.greedy_service import GreedyService


class RecommendationService:

    @staticmethod
    def generate(db, request):

        # ==========================================
        # 1. AMBIL SEMUA DATA WISATA
        # ==========================================

        wisata = WisataRepository.get_all(db)

        # ==========================================
        # 2. CONTENT-BASED RECOMMENDATION
        # ==========================================

        ranking = TFIDFService.recommend(
            request.preferensi,
            wisata
        )
        print("\n========== TOP 10 TF-IDF ==========")

        for i, item in enumerate(ranking[:10], start=1):
            print(
                f"{i}. {item['nama_wisata']} "
                f"| {item['kategori']} "
                f"| similarity={item['similarity']:.4f}"
            )

        print("===================================\n")
        # ==========================================
        # 3. GREEDY PEMILIHAN DESTINASI
        # ==========================================

        itinerary = GreedyService.select_destinations(
            ranking,
            request.budget,
            request.jumlah_orang,
            request.jumlah_destinasi
        )

        # ==========================================
        # 4. GREEDY PENYUSUNAN RUTE
        # ==========================================

        itinerary, total_distance = GreedyService.optimize_route(
            itinerary,
            request.latitude,
            request.longitude
        )

        # ==========================================
        # 5. HITUNG TOTAL BIAYA DAN DURASI
        # ==========================================

        total_biaya = 0
        total_durasi = 0

        for wisata in itinerary:

            harga = float(wisata["harga_min"])

            total_biaya += (
                harga * request.jumlah_orang
            )

            total_durasi += (
                wisata["estimasi_durasi"]
            )

        # ==========================================
        # 6. RESPONSE
        # ==========================================

        return {
            "summary": {
                "jumlah_destinasi": len(itinerary),
                "total_biaya": int(total_biaya),
                "total_durasi": total_durasi,
                "total_jarak_km": total_distance
            },
            "itinerary": itinerary
        }

    @staticmethod
    def recommend(db, request):

        return RecommendationService.generate(
            db,
            request
        )