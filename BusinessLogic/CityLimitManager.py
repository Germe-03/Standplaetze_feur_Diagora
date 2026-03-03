from datetime import date
from typing import List, Optional

from DataAccess.CitiesDataAccess import CitiesDataAccess
from DataAccess.CityLimitDataAccess import CityLimitDataAccess
from Model.CityLimit import CityLimit


class CityLimitManager:
    def __init__(self, db_path: str = None):
        self.city_limit_dao = CityLimitDataAccess(db_path)
        self.cities_dao = CitiesDataAccess(db_path)

    def create_city_limit(
        self,
        city_limit_yearly: int,
        city_limit_monthly: int,
        city_limit_campaign: int,
        city_limit_yearly_per_l: int,
        city_limit_monthly_per_l: int,
        city_limit_campaign_per_l: int,
        valid_from: date,
        unlimited: bool,
        city_id: int,
    ) -> CityLimit:
        """
        Erstellt ein neues Stadt-Limit mit Validierung der Geschäftsregeln
        """
        self._validate_city_limit_data(
            city_limit_yearly,
            city_limit_monthly,
            city_limit_campaign,
            city_limit_yearly_per_l,
            city_limit_monthly_per_l,
            city_limit_campaign_per_l,
            valid_from,
            unlimited,
            city_id,
        )

        city = self.cities_dao.get_city_by_id(city_id)
        if not city:
            raise ValueError("Stadt existiert nicht")

        return self.city_limit_dao.insert_city_limit(
            city_limit_yearly,
            city_limit_monthly,
            city_limit_campaign,
            city_limit_yearly_per_l,
            city_limit_monthly_per_l,
            city_limit_campaign_per_l,
            valid_from,
            unlimited,
            city_id,
        )

    def get_city_limit_by_id(self, city_limit_id: int) -> Optional[CityLimit]:
        """
        Holt ein Stadt-Limit nach ID
        """
        if not city_limit_id or city_limit_id <= 0:
            raise ValueError("Ungültige CityLimit-ID")
        return self.city_limit_dao.get_city_limit_by_id(city_limit_id)

    def get_city_limits_by_city_name(self, city_name: str) -> List[CityLimit]:
        """
        Holt alle Stadt-Limits zu einem Stadtnamen
        """
        if not city_name or not city_name.strip():
            raise ValueError("Stadtname muss angegeben werden")
        return self.city_limit_dao.get_city_limit_by_city_name(city_name.strip())

    def get_city_limits_by_unlimited(self, unlimited: bool) -> List[CityLimit]:
        """
        Holt alle Stadt-Limits nach Unlimited-Flag
        """
        if not isinstance(unlimited, bool):
            raise ValueError("Unlimited muss bool sein")
        return self.city_limit_dao.get_city_limits_by_unlimited(unlimited)

    def update_city_limit(self, city_limit: CityLimit) -> None:
        """
        Aktualisiert ein bestehendes Stadt-Limit
        """
        if not city_limit or not city_limit.city_limit_id:
            raise ValueError("Ungültiges Stadt-Limit")

        existing_city_limit = self.city_limit_dao.get_city_limit_by_id(city_limit.city_limit_id)
        if not existing_city_limit:
            raise ValueError("Stadt-Limit existiert nicht")

        city = self.cities_dao.get_city_by_id(city_limit.city_id)
        if not city:
            raise ValueError("Stadt existiert nicht")

        self.city_limit_dao.update_city_limit(city_limit)

    def delete_city_limit(self, city_limit_id: int) -> None:
        """
        Löscht ein Stadt-Limit
        """
        if not city_limit_id or city_limit_id <= 0:
            raise ValueError("Ungültige CityLimit-ID")

        existing_city_limit = self.city_limit_dao.get_city_limit_by_id(city_limit_id)
        if not existing_city_limit:
            raise ValueError("Stadt-Limit existiert nicht")

        self.city_limit_dao.delete_city_limit(city_limit_id)

    def validate_city_limit_exists(self, city_limit_id: int) -> bool:
        """
        Prüft ob ein Stadt-Limit existiert
        """
        if not city_limit_id or city_limit_id <= 0:
            return False
        return self.city_limit_dao.get_city_limit_by_id(city_limit_id) is not None

    def _validate_city_limit_data(
        self,
        city_limit_yearly: int,
        city_limit_monthly: int,
        city_limit_campaign: int,
        city_limit_yearly_per_l: int,
        city_limit_monthly_per_l: int,
        city_limit_campaign_per_l: int,
        valid_from: date,
        unlimited: bool,
        city_id: int,
    ) -> None:
        """
        Validiert Stadt-Limit-Daten nach Geschäftsregeln
        """
        if not isinstance(unlimited, bool):
            raise ValueError("Unlimited muss bool sein")
        if not valid_from:
            raise ValueError("ValidFrom ist ein Pflichtfeld")
        if not city_id or city_id <= 0:
            raise ValueError("Stadt ist ein Pflichtfeld")

        number_fields = [
            city_limit_yearly,
            city_limit_monthly,
            city_limit_campaign,
            city_limit_yearly_per_l,
            city_limit_monthly_per_l,
            city_limit_campaign_per_l,
        ]
        for value in number_fields:
            if value is not None and value < 0:
                raise ValueError("Limits dürfen nicht negativ sein")
