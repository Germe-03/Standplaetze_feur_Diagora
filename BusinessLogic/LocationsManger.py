from typing import List, Optional, Dict

from DataAccess.CitiesDataAccess import CitiesDataAccess
from DataAccess.LocationsDataAccess import LocationsDataAccess
from DataAccess.UserDataAccess import UserDataAccess
from Model.Location import Location


class LocationsManger:
    def __init__(self, db_path: str = None):
        self.locations_dao = LocationsDataAccess(db_path)
        self.cities_dao = CitiesDataAccess(db_path)
        self.user_dao = UserDataAccess(db_path)

    def create_location(
        self,
        name: str,
        is_sbb: bool,
        max_dialog: int,
        rating: int,
        note: str,
        price: float,
        city_id: int,
        user_id: int,
    ) -> Location:
        """
        Erstellt einen neuen Standort mit Validierung der Geschäftsregeln
        """
        self._validate_location_data(name, is_sbb, max_dialog, rating, price, city_id, user_id)

        city = self.cities_dao.get_city_by_id(city_id)
        if not city:
            raise ValueError("Stadt existiert nicht")

        user = self.user_dao.get_user_by_id(user_id)
        if not user:
            raise ValueError("Benutzer existiert nicht")

        return self.locations_dao.insert_location(
            name.strip(), is_sbb, max_dialog, rating, note, price, city_id, user_id
        )

    def get_location_by_id(self, location_id: int) -> Optional[Location]:
        """
        Holt einen Standort nach ID
        """
        if not location_id or location_id <= 0:
            raise ValueError("Ungültige Location-ID")
        return self.locations_dao.get_location_by_id(location_id)

    def get_locations_by_name(self, name: str) -> List[Location]:
        """
        Holt Standorte mit einem bestimmten Namen
        """
        if not name or not name.strip():
            raise ValueError("Standortname muss angegeben werden")
        return self.locations_dao.get_location_by_name(name.strip())

    def get_locations_by_city_id(self, city_id: int) -> List[Location]:
        """
        Holt Standorte einer Stadt-ID
        """
        if not city_id or city_id <= 0:
            raise ValueError("Ungültige City-ID")
        return self.locations_dao.get_locations_by_city_id(city_id)

    def get_locations_by_city_name(self, city_name: str) -> List[Location]:
        """
        Holt Standorte anhand des Stadtnamens
        """
        if not city_name or not city_name.strip():
            raise ValueError("Stadtname muss angegeben werden")
        return self.locations_dao.get_locations_by_city_name(city_name.strip())

    def get_locations_by_user(self, user_id: int) -> List[Location]:
        """
        Holt Standorte eines Benutzers
        """
        if not user_id or user_id <= 0:
            raise ValueError("Ungültige User-ID")
        return self.locations_dao.get_locations_by_user_id(user_id)

    def get_locations_by_is_sbb(self, is_sbb: bool) -> List[Location]:
        """
        Holt Standorte anhand des SBB-Flags
        """
        if not isinstance(is_sbb, bool):
            raise ValueError("IsSBB muss bool sein")
        return self.locations_dao.get_locations_by_is_sbb(is_sbb)

    def get_locations_by_rating(self, min_rating: int, max_rating: int) -> List[Location]:
        """
        Holt Standorte in einem Rating-Bereich
        """
        if min_rating < 0 or max_rating < 0:
            raise ValueError("Ratings dürfen nicht negativ sein")
        if min_rating > max_rating:
            raise ValueError("MinRating muss kleiner als MaxRating sein")
        return self.locations_dao.get_locations_by_rating(min_rating, max_rating)

    def get_locations_by_price_range(self, min_price: float, max_price: float) -> List[Location]:
        """
        Holt Standorte in einem Preisbereich
        """
        if min_price < 0 or max_price < 0:
            raise ValueError("Preise dürfen nicht negativ sein")
        if min_price > max_price:
            raise ValueError("MinPrice muss kleiner als MaxPrice sein")
        return self.locations_dao.get_locations_by_price_range(min_price, max_price)

    def update_location(self, location: Location) -> None:
        """
        Aktualisiert einen bestehenden Standort
        """
        if not location or not location.location_id:
            raise ValueError("Ungültiger Standort")

        existing_location = self.locations_dao.get_location_by_id(location.location_id)
        if not existing_location:
            raise ValueError("Standort existiert nicht")

        self.locations_dao.update_location(location)

    def delete_location(self, location_id: int) -> None:
        """
        Löscht einen Standort
        """
        if not location_id or location_id <= 0:
            raise ValueError("Ungültige Location-ID")

        existing_location = self.locations_dao.get_location_by_id(location_id)
        if not existing_location:
            raise ValueError("Standort existiert nicht")

        self.locations_dao.delete_location(location_id)

    def validate_location_exists(self, location_id: int) -> bool:
        """
        Prüft ob ein Standort existiert
        """
        if not location_id or location_id <= 0:
            return False
        return self.locations_dao.get_location_by_id(location_id) is not None

    def get_location_statistics(self) -> Dict:
        """
        Gibt einfache Standort-Statistiken zurück
        """
        sbb_locations = self.get_locations_by_is_sbb(True)
        non_sbb_locations = self.get_locations_by_is_sbb(False)
        all_locations = sbb_locations + non_sbb_locations

        prices = [float(l.price) for l in all_locations if l.price is not None]
        ratings = [int(l.rating) for l in all_locations if l.rating is not None]

        return {
            "total_locations": len(all_locations),
            "sbb_locations": len(sbb_locations),
            "non_sbb_locations": len(non_sbb_locations),
            "average_price": round(sum(prices) / len(prices), 2) if prices else 0.0,
            "average_rating": round(sum(ratings) / len(ratings), 2) if ratings else 0.0,
        }

    def _validate_location_data(
        self,
        name: str,
        is_sbb: bool,
        max_dialog: int,
        rating: int,
        price: float,
        city_id: int,
        user_id: int,
    ) -> None:
        """
        Validiert Standortdaten nach Geschäftsregeln
        """
        if not name or not name.strip():
            raise ValueError("Standortname ist ein Pflichtfeld")
        if len(name.strip()) < 2:
            raise ValueError("Standortname muss mindestens 2 Zeichen lang sein")

        if not isinstance(is_sbb, bool):
            raise ValueError("IsSBB muss bool sein")

        if not isinstance(max_dialog, int) or max_dialog <= 0:
            raise ValueError("MaxDialog muss eine positive ganze Zahl sein")

        if not isinstance(rating, int) or rating < 0 or rating > 5:
            raise ValueError("Rating muss zwischen 0 und 5 liegen")

        if price is not None and price < 0:
            raise ValueError("Preis darf nicht negativ sein")

        if not city_id or city_id <= 0:
            raise ValueError("Stadt ist ein Pflichtfeld")
        if not user_id or user_id <= 0:
            raise ValueError("Benutzer ist ein Pflichtfeld")
