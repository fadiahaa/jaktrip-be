from app.models.itinerary import Itinerary
from app.models.itinerary_detail import ItineraryDetail


class ItineraryRepository:

    @staticmethod
    def create(db, itinerary: Itinerary):

        db.add(itinerary)
        db.flush()
        db.refresh(itinerary)

        return itinerary

    @staticmethod
    def create_detail(db, detail: ItineraryDetail):

        db.add(detail)