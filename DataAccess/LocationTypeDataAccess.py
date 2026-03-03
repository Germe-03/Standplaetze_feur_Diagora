import sqlite3

from DataAccess.BaseDataAccess import BaseDataAccess
from Model.LocationType import LocationType


class LocationTypeDataAccess(BaseDataAccess):
    def __init__(self, db_path: str = None):
        super().__init__(db_path)

    def get_location_type_by_id(self, location_type_id: int) -> LocationType | None:
        sql = """
        select LocationTypeID, LocationType, UserID
        from LocationType
        where LocationTypeID = ?   
        """
        row = self.fetchone(sql, (location_type_id,))
        if row:
            return LocationType(*row)
        return None

    def get_location_type_by_name(self, location_type: str) -> list[LocationType]:
        sql = """
        select LocationTypeID, LocationType, UserID
        from LocationType
        where LocationType = ?
        """
        rows = self.fetchall(sql, (location_type,))
        return [LocationType(*row) for row in rows]

    def get_location_types_by_user_id(self, user_id: int) -> list[LocationType]:
        sql = """
        select LocationTypeID, LocationType, UserID
        from LocationType
        where UserID = ?
        """
        rows = self.fetchall(sql, (user_id,))
        return [LocationType(*row) for row in rows]

    def get_all_location_types(self) -> list[LocationType]:
        sql = """
        select LocationTypeID, LocationType, UserID
        from LocationType
        order by LocationType
        """
        rows = self.fetchall(sql)
        return [LocationType(*row) for row in rows]

    def insert_location_type(self, location_type: str, user_id: int) -> LocationType:
        sql = """
        INSERT INTO LocationType (LocationType, UserID)
        VALUES (?, ?)
        """
        new_id, _ = self.execute(sql, (location_type, user_id))
        return LocationType(new_id, location_type, user_id)

    def update_location_type(self, location_type_obj: LocationType) -> None:
        sql = """
        UPDATE LocationType
        SET LocationType = ?, UserID = ?
        WHERE LocationTypeID = ?
        """
        self.execute(sql, (location_type_obj.location_type, location_type_obj.user_id, location_type_obj.location_type_id))

    def delete_location_type(self, location_type_id: int) -> None:
        sql = "DELETE FROM LocationTypes WHERE LocationTypeID = ?"
        self.execute(sql, (location_type_id,))
