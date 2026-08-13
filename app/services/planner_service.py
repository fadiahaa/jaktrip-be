from app.models.planner import Planner
from app.models.itinerary import Itinerary
from app.models.itinerary_detail import ItineraryDetail

from app.repositories.planner_repository import PlannerRepository
from app.repositories.itinerary_repository import ItineraryRepository

from app.services.recommendation_service import RecommendationService


class PlannerService:

    @staticmethod
    def save(
        db,
        user_id,
        request
    ):

        try:

            # ==========================
            # Simpan Planner
            # ==========================

            planner = Planner(

                id_user=user_id,

                preferensi=request.preferensi,

                budget=request.budget,

                jumlah_orang=request.jumlah_orang,

                jumlah_destinasi=request.jumlah_destinasi,

                latitude=request.latitude,

                longitude=request.longitude

            )

            PlannerRepository.create(
                db,
                planner
            )

            # ==========================
            # Generate Itinerary
            # ==========================

            result = RecommendationService.generate(
                db,
                request
            )

            summary = result["summary"]

            itinerary_result = result["itinerary"]

            # ==========================
            # Simpan Itinerary
            # ==========================

            itinerary = Itinerary(

                id_planner=planner.id_planner,

                total_biaya=summary["total_biaya"],

                sisa_budget=request.budget - summary["total_biaya"],

                total_durasi=summary["total_durasi"],

                total_jarak=summary["total_jarak_km"]

            )

            ItineraryRepository.create(
                db,
                itinerary
            )

            # ==========================
            # Simpan Detail
            # ==========================

            for index, wisata in enumerate(itinerary_result):

                detail = ItineraryDetail(

                    id_itinerary=itinerary.id_itinerary,

                    id_wisata=wisata["id_wisata"],

                    urutan=index + 1,

                    estimasi_datang=None,

                    estimasi_selesai=None

                )

                ItineraryRepository.create_detail(
                    db,
                    detail
                )

            # ==========================
            # Commit
            # ==========================

            db.commit()

            return result

        except Exception as e:

            db.rollback()

            raise
        
    @staticmethod
    def history(
        db,
        user_id
    ):

        data = PlannerRepository.get_history(
            db,
            user_id
        )

        result = []

        for planner, itinerary in data:

            result.append({

                "id_planner": planner.id_planner,

                "preferensi": planner.preferensi,

                "budget": float(planner.budget),

                "jumlah_orang": planner.jumlah_orang,

                "jumlah_destinasi": planner.jumlah_destinasi,

                "created_at": planner.created_at,

                "total_biaya": float(itinerary.total_biaya),

                "sisa_budget": float(itinerary.sisa_budget),

                "total_durasi": itinerary.total_durasi,

                "total_jarak": float(itinerary.total_jarak)

            })

        return result
    
    @staticmethod
    def detail(
        db,
        planner_id,
        user_id
    ):

        data = PlannerRepository.get_detail(
            db,
            planner_id,
            user_id
        )

        if not data:
            raise Exception("Planner tidak ditemukan")

        planner = data[0][0]
        itinerary = data[0][1]

        wisata_list = []

        for _, _, detail, wisata in data:

            wisata_list.append({

                "urutan": detail.urutan,

                "id_wisata": wisata.id_wisata,

                "nama_wisata": wisata.nama_wisata,

                "kategori": wisata.kategori,

                "alamat": wisata.alamat,

                "harga_min": float(wisata.harga_min),

                "harga_max": float(wisata.harga_max),

                "estimasi_durasi": wisata.estimasi_durasi,

                "latitude": float(wisata.latitude),

                "longitude": float(wisata.longitude),

                "rating": float(wisata.rating)

                if wisata.rating is not None else None,

                "gambar": wisata.gambar

            })

        return {

            "summary": {

                "id_planner": planner.id_planner,

                "preferensi": planner.preferensi,

                "budget": float(planner.budget),

                "jumlah_orang": planner.jumlah_orang,

                "jumlah_destinasi": planner.jumlah_destinasi,

                "total_biaya": float(itinerary.total_biaya),

                "sisa_budget": float(itinerary.sisa_budget),

                "total_durasi": itinerary.total_durasi,

                "total_jarak": float(itinerary.total_jarak)

            },

            "itinerary": wisata_list

        }
        
    @staticmethod
    def delete(db, planner_id, user_id):

        planner = PlannerRepository.get_by_id(
            db,
            planner_id,
            user_id
        )

        if planner is None:
            raise Exception("Planner tidak ditemukan")

        try:

            PlannerRepository.delete(
                db,
                planner
            )

            db.commit()

            return {
                "message": "Planner berhasil dihapus"
            }

        except Exception:

            db.rollback()

            raise