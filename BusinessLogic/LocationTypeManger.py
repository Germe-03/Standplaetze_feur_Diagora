from typing import List, Optional

from DataAccess.LocationTypeDataAccess import LocationTypeDataAccess
from DataAccess.UserDataAccess import UserDataAccess
from Model.LocationType import LocationType


class LocationTypeManger:
    def __init__(self, db_path: str = None):
        self.location_type_dao = LocationTypeDataAccess(db_path)
        self.user_dao = UserDataAccess(db_path)

    def create_location_type(self, location_type: str, user_id: int) -> LocationType:
        """
        Erstellt einen neuen Standorttyp mit Validierung der Geschäftsregeln
        """
        self._validate_location_type_data(location_type, user_id)

        user = self.user_dao.get_user_by_id(user_id)
        if not user:
            raise ValueError("Benutzer existiert nicht")

        existing_types = self.location_type_dao.get_location_type_by_name(location_type.strip())
        if any(lt.user_id == user_id for lt in existing_types):
            raise ValueError("Dieser Standorttyp existiert für den Benutzer bereits")

        return self.location_type_dao.insert_location_type(location_type.strip(), user_id)

    def get_location_type_by_id(self, location_type_id: int) -> Optional[LocationType]:
        """
        Holt einen Standorttyp nach ID
        """
        if not location_type_id or location_type_id <= 0:
            raise ValueError("Ungültige LocationType-ID")
        return self.location_type_dao.get_location_type_by_id(location_type_id)

    def get_location_types_by_name(self, location_type: str) -> List[LocationType]:
        """
        Holt Standorttypen mit bestimmtem Namen
        """
        if not location_type or not location_type.strip():
            raise ValueError("LocationType muss angegeben werden")
        return self.location_type_dao.get_location_type_by_name(location_type.strip())

    def get_location_types_by_user(self, user_id: int) -> List[LocationType]:
        """
        Holt Standorttypen eines Benutzers
        """
        if not user_id or user_id <= 0:
            raise ValueError("Ungültige User-ID")
        return self.location_type_dao.get_location_types_by_user_id(user_id)

    def get_all_location_types(self) -> List[LocationType]:
        """
        Holt alle Standorttypen
        """
        return self.location_type_dao.get_all_location_types()

    def update_location_type(self, location_type_obj: LocationType) -> None:
        """
        Aktualisiert einen bestehenden Standorttyp
        """
        if not location_type_obj or not location_type_obj.location_type_id:
            raise ValueError("Ungültiger Standorttyp")

        existing_type = self.location_type_dao.get_location_type_by_id(location_type_obj.location_type_id)
        if not existing_type:
            raise ValueError("Standorttyp existiert nicht")

        self.location_type_dao.update_location_type(location_type_obj)

    def delete_location_type(self, location_type_id: int) -> None:
        """
        Löscht einen Standorttyp
        """
        if not location_type_id or location_type_id <= 0:
            raise ValueError("Ungültige LocationType-ID")

        existing_type = self.location_type_dao.get_location_type_by_id(location_type_id)
        if not existing_type:
            raise ValueError("Standorttyp existiert nicht")

        self.location_type_dao.delete_location_type(location_type_id)

    def validate_location_type_exists(self, location_type_id: int) -> bool:
        """
        Prüft ob ein Standorttyp existiert
        """
        if not location_type_id or location_type_id <= 0:
            return False
        return self.location_type_dao.get_location_type_by_id(location_type_id) is not None

    def _validate_location_type_data(self, location_type: str, user_id: int) -> None:
        """
        Validiert Standorttyp-Daten nach Geschäftsregeln
        """
        if not location_type or not location_type.strip():
            raise ValueError("LocationType ist ein Pflichtfeld")
        if len(location_type.strip()) < 2:
            raise ValueError("LocationType muss mindestens 2 Zeichen lang sein")
        if not user_id or user_id <= 0:
            raise ValueError("Benutzer ist ein Pflichtfeld")
