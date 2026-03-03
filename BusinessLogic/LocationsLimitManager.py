from datetime import date
from typing import List, Optional

from DataAccess.LocationLimitsDataAccess import LocationLimitsDataAccess
from DataAccess.LocationsDataAccess import LocationsDataAccess
from DataAccess.UserDataAccess import UserDataAccess
from Model.LocationLimit import LocationLimit


class LocationsLimitManager:
    def __init__(self, db_path: str = None):
        self.location_limit_dao = LocationLimitsDataAccess(db_path)
        self.locations_dao = LocationsDataAccess(db_path)
        self.user_dao = UserDataAccess(db_path)

    def create_location_limit(
        self,
        location_limit_yearly: int,
        location_limit_monthly: int,
        location_limit_campaign: int,
        location_id: int,
        valid_from: date,
        user_id: int,
    ) -> LocationLimit:
        """
        Erstellt ein neues Standort-Limit mit Validierung der Geschäftsregeln
        """
        self._validate_location_limit_data(
            location_limit_yearly,
            location_limit_monthly,
            location_limit_campaign,
            location_id,
            valid_from,
            user_id,
        )

        location = self.locations_dao.get_location_by_id(location_id)
        if not location:
            raise ValueError("Standort existiert nicht")

        user = self.user_dao.get_user_by_id(user_id)
        if not user:
            raise ValueError("Benutzer existiert nicht")

        return self.location_limit_dao.insert_location_limit(
            location_limit_yearly,
            location_limit_monthly,
            location_limit_campaign,
            location_id,
            valid_from,
            user_id,
        )

    def get_location_limit_by_id(self, location_limit_id: int) -> Optional[LocationLimit]:
        """
        Holt ein Standort-Limit nach ID
        """
        if not location_limit_id or location_limit_id <= 0:
            raise ValueError("Ungültige LocationLimit-ID")
        return self.location_limit_dao.get_location_limit_by_id(location_limit_id)

    def get_location_limits_by_location_name(self, location_name: str) -> List[LocationLimit]:
        """
        Holt Standort-Limits per Standortname
        """
        if not location_name or not location_name.strip():
            raise ValueError("Standortname muss angegeben werden")
        return self.location_limit_dao.get_location_limit_by_location_name(location_name.strip())

    def get_location_limits_by_user(self, user_id: int) -> List[LocationLimit]:
        """
        Holt Standort-Limits eines Benutzers
        """
        if not user_id or user_id <= 0:
            raise ValueError("Ungültige User-ID")
        return self.location_limit_dao.get_location_limits_by_user_id(user_id)

    def get_location_limits_by_location_id(self, location_id: int) -> List[LocationLimit]:
        """
        Holt Standort-Limits einer Location-ID
        """
        if not location_id or location_id <= 0:
            raise ValueError("Ungültige Location-ID")
        return self.location_limit_dao.get_location_limits_by_location_id(location_id)

    def get_location_limits_by_valid_from(self, valid_from: date) -> List[LocationLimit]:
        """
        Holt Standort-Limits nach Gültigkeitsdatum
        """
        if not valid_from:
            raise ValueError("ValidFrom muss angegeben werden")
        return self.location_limit_dao.get_location_limits_by_valid_from(valid_from)

    def update_location_limit(self, location_limit: LocationLimit) -> None:
        """
        Aktualisiert ein bestehendes Standort-Limit
        """
        if not location_limit or not location_limit.location_limit_id:
            raise ValueError("Ungültiges Standort-Limit")

        existing_limit = self.location_limit_dao.get_location_limit_by_id(location_limit.location_limit_id)
        if not existing_limit:
            raise ValueError("Standort-Limit existiert nicht")

        self.location_limit_dao.update_location_limit(location_limit)

    def delete_location_limit(self, location_limit_id: int) -> None:
        """
        Löscht ein Standort-Limit
        """
        if not location_limit_id or location_limit_id <= 0:
            raise ValueError("Ungültige LocationLimit-ID")

        existing_limit = self.location_limit_dao.get_location_limit_by_id(location_limit_id)
        if not existing_limit:
            raise ValueError("Standort-Limit existiert nicht")

        self.location_limit_dao.delete_location_limit(location_limit_id)

    def validate_location_limit_exists(self, location_limit_id: int) -> bool:
        """
        Prüft ob ein Standort-Limit existiert
        """
        if not location_limit_id or location_limit_id <= 0:
            return False
        return self.location_limit_dao.get_location_limit_by_id(location_limit_id) is not None

    def _validate_location_limit_data(
        self,
        location_limit_yearly: int,
        location_limit_monthly: int,
        location_limit_campaign: int,
        location_id: int,
        valid_from: date,
        user_id: int,
    ) -> None:
        """
        Validiert Standort-Limit-Daten nach Geschäftsregeln
        """
        if not valid_from:
            raise ValueError("ValidFrom ist ein Pflichtfeld")
        if not location_id or location_id <= 0:
            raise ValueError("Standort ist ein Pflichtfeld")
        if not user_id or user_id <= 0:
            raise ValueError("Benutzer ist ein Pflichtfeld")

        for value in (location_limit_yearly, location_limit_monthly, location_limit_campaign):
            if value is not None and value < 0:
                raise ValueError("Limits dürfen nicht negativ sein")
