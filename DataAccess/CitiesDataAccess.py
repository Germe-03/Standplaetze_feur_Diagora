from DataAccess.BaseDataAccess import BaseDataAccess
from Model.City import City


class CitiesDataAccess(BaseDataAccess):
    def __init__(self, db_path: str = None):
        super().__init__(db_path)

    def get_city_by_id(self, city_id: int) -> City | None:
        sql = """
        select CityID, Name, StateID
        from Cities
        where CityID = ?   
        """
        row = self.fetchone(sql, (city_id,))
        if row:
            return City(*row)
        return None

    def get_city_by_name(self, name: str) -> list[City]:
        sql = """
        select CityID, Name, StateID
        from Cities
        where Name = ?
        """
        rows = self.fetchall(sql, (name,))
        return [City(*row) for row in rows]

    def get_cities_by_state_id(self, state_id: int) -> list[City]:
        sql = """
        select CityID, Name, StateID
        from Cities
        where StateID = ?
        """
        rows = self.fetchall(sql, (state_id,))
        return [City(*row) for row in rows]

    def insert_city(self, name: str, state_id: int) -> City:
        sql = """
        INSERT INTO Cities (Name, StateID)
        VALUES (?, ?)
        """
        new_id, _ = self.execute(sql, (name, state_id))
        return City(new_id, name, state_id)

    def update_city(self, city: City) -> None:
        sql = """
        UPDATE Cities
        SET Name = ?, StateID = ?
        WHERE CityID = ?
        """
        self.execute(sql, (city.name, city.state_id, city.city_id))

    def delete_city(self, city_id: int) -> None:
        sql = "DELETE FROM Cities WHERE CityID = ?"
        self.execute(sql, (city_id,))
