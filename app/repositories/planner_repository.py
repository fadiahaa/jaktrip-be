from app.models.planner import Planner
from app.models.itinerary import Itinerary
from app.models.itinerary import Itinerary
from app.models.itinerary_detail import ItineraryDetail
from app.models.wisata import Wisata

class PlannerRepository:

    @staticmethod
    def create(db, planner: Planner):

        db.add(planner)
        db.flush()
        db.refresh(planner)

        return planner
    
    @staticmethod
    def get_history(
        db,
        user_id
    ):

        return (

            db.query(
                Planner,
                Itinerary
            )

            .join(
                Itinerary,
                Planner.id_planner == Itinerary.id_planner
            )

            .filter(
                Planner.id_user == user_id
            )

            .order_by(
                Planner.created_at.desc()
            )

            .all()

        )
        
        
    @staticmethod
    def get_detail(
        db,
        planner_id,
        user_id
    ):

        return (

            db.query(
                Planner,
                Itinerary,
                ItineraryDetail,
                Wisata
            )

            .join(
                Itinerary,
                Planner.id_planner == Itinerary.id_planner
            )

            .join(
                ItineraryDetail,
                Itinerary.id_itinerary == ItineraryDetail.id_itinerary
            )

            .join(
                Wisata,
                ItineraryDetail.id_wisata == Wisata.id_wisata
            )

            .filter(
                Planner.id_planner == planner_id,
                Planner.id_user == user_id
            )

            .order_by(
                ItineraryDetail.urutan.asc()
            )

            .all()

        )
        
    @staticmethod
    def delete(
        db,
        planner
    ):

        db.delete(planner)

        db.commit()
        
    @staticmethod
    def get_by_id(
        db,
        planner_id,
        user_id
    ):

        return (

            db.query(Planner)

            .filter(
                Planner.id_planner == planner_id,
                Planner.id_user == user_id
            )

            .first()

        )