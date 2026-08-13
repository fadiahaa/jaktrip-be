from itertools import permutations
from math import radians, sin, cos, sqrt, atan2


class GreedyService:

    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):

        R = 6371

        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)

        a = (
            sin(dlat / 2) ** 2
            + cos(radians(lat1))
            * cos(radians(lat2))
            * sin(dlon / 2) ** 2
        )

        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return R * c

    @staticmethod
    def select_destinations(
        ranking,
        budget,
        jumlah_orang,
        jumlah_destinasi
    ):

        itinerary = []
        budget_sisa = float(budget)

        for wisata in ranking:

            harga_min = float(wisata["harga_min"])

            total_harga = harga_min * jumlah_orang

            if total_harga > budget_sisa:
                continue

            itinerary.append(wisata)

            budget_sisa -= total_harga

            if len(itinerary) >= jumlah_destinasi:
                break

        return itinerary

    @staticmethod
    def optimize_route(
        itinerary,
        user_lat=None,
        user_lon=None
    ):

        # ==========================================
        # VALIDASI LOKASI USER
        # ==========================================
        # latitude = 0 dan longitude = 0 berarti
        # user tidak mengaktifkan lokasi.
        if (
            user_lat is None
            or user_lon is None
            or (user_lat == 0 and user_lon == 0)
        ):
            user_lat = None
            user_lon = None

        # ==========================================
        # JIKA 0 ATAU 1 DESTINASI
        # ==========================================
        if len(itinerary) <= 1:

            if len(itinerary) == 1:
                itinerary[0]["distance_km"] = 0

            return itinerary, 0

        # ==========================================
        # CARI URUTAN DENGAN JARAK TERPENDEK
        # ==========================================

        from itertools import permutations

        best_route = None
        best_distance = float("inf")

        for route in permutations(itinerary):

            total_distance = 0

            # --------------------------------------
            # Jika lokasi user tersedia,
            # hitung jarak dari lokasi user
            # ke destinasi pertama.
            # --------------------------------------

            if user_lat is not None and user_lon is not None:

                total_distance += GreedyService.calculate_distance(
                    user_lat,
                    user_lon,
                    route[0]["latitude"],
                    route[0]["longitude"]
                )

            # --------------------------------------
            # Hitung jarak antar destinasi
            # --------------------------------------

            for i in range(len(route) - 1):

                total_distance += GreedyService.calculate_distance(
                    route[i]["latitude"],
                    route[i]["longitude"],
                    route[i + 1]["latitude"],
                    route[i + 1]["longitude"]
                )

            # --------------------------------------
            # Simpan rute terpendek
            # --------------------------------------

            if total_distance < best_distance:

                best_distance = total_distance
                best_route = list(route)

        # ==========================================
        # HITUNG JARAK SETIAP PERJALANAN
        # ==========================================

        optimized = []

        previous_lat = user_lat
        previous_lon = user_lon

        for wisata in best_route:

            # Kalau tidak ada lokasi user,
            # destinasi pertama dianggap titik awal.
            if previous_lat is None or previous_lon is None:

                distance = 0

            else:

                distance = GreedyService.calculate_distance(
                    previous_lat,
                    previous_lon,
                    wisata["latitude"],
                    wisata["longitude"]
                )

            wisata["distance_km"] = round(distance, 2)

            optimized.append(wisata)

            previous_lat = wisata["latitude"]
            previous_lon = wisata["longitude"]

        return optimized, round(best_distance, 2)