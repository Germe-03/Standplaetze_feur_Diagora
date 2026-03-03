from DataAccess.BaseDataAccess import BaseDataAccess
from Model.Location import Location


class LocationsDataAccess(BaseDataAccess):
    def __init__(self, db_path: str = None):
        super().__init__(db_path)

    def get_all_locations(self) -> list[Location]:
        sql = """
        select LocationID, Name, IsSBB, MaxDialog, Rating, Notes, Price, CityID, UserID
        from Locations
        order by Name
        """
        rows = self.fetchall(sql)
        return [Location(*row) for row in rows]

    def get_location_by_id(self, location_id: int) -> Location | None:
        sql = """
        select LocationID, Name, IsSBB, MaxDialog, Rating, Notes, Price, CityID, UserID
        from Locations
        where LocationID = ?   
        """
        row = self.fetchone(sql, (location_id,))
        if row:
            return Location(*row)
        return None

    def get_location_by_name(self, name: str) -> list[Location]:
        sql = """
        select LocationID, Name, IsSBB, MaxDialog, Rating, Notes, Price, CityID, UserID
        from Locations
        where Name = ?
        """
        rows = self.fetchall(sql, (name,))
        return [Location(*row) for row in rows]

    def get_locations_by_city_id(self, city_id: int) -> list[Location]:
        sql = """
        select LocationID, Name, IsSBB, MaxDialog, Rating, Notes, Price, CityID, UserID
        from Locations
        where CityID = ?
        """
        rows = self.fetchall(sql, (city_id,))
        return [Location(*row) for row in rows]

    def get_locations_by_city_name(self, city_name: str) -> list[Location]:
        sql = """
        select l.LocationID, l.Name, l.IsSBB, l.MaxDialog, l.Rating, l.Notes, l.Price, l.CityID, l.UserID
        from Locations l
        join Cities c on c.CityID = l.CityID
        where c.Name = ?
        """
        rows = self.fetchall(sql, (city_name,))
        return [Location(*row) for row in rows]

    def get_locations_by_user_id(self, user_id: int) -> list[Location]:
        sql = """
        select LocationID, Name, IsSBB, MaxDialog, Rating, Notes, Price, CityID, UserID
        from Locations
        where UserID = ?
        """
        rows = self.fetchall(sql, (user_id,))
        return [Location(*row) for row in rows]

    def get_locations_by_is_sbb(self, is_sbb: bool) -> list[Location]:
        sql = """
        select LocationID, Name, IsSBB, MaxDialog, Rating, Notes, Price, CityID, UserID
        from Locations
        where IsSBB = ?
        """
        rows = self.fetchall(sql, (is_sbb,))
        return [Location(*row) for row in rows]

    def get_locations_by_rating(self, min_rating: int, max_rating: int) -> list[Location]:
        sql = """
        select LocationID, Name, IsSBB, MaxDialog, Rating, Notes, Price, CityID, UserID
        from Locations
        where Rating between ? and ?
        """
        rows = self.fetchall(sql, (min_rating, max_rating))
        return [Location(*row) for row in rows]

    def get_locations_by_price_range(self, min_price: float, max_price: float) -> list[Location]:
        sql = """
        select LocationID, Name, IsSBB, MaxDialog, Rating, Notes, Price, CityID, UserID
        from Locations
        where Price between ? and ?
        """
        rows = self.fetchall(sql, (min_price, max_price))
        return [Location(*row) for row in rows]

    def insert_location(self, name: str, is_sbb: bool, max_dialog: int, rating: int, 
                       note: str, price: float, city_id: int, user_id: int) -> Location:
        sql = """
        INSERT INTO Locations (Name, IsSBB, MaxDialog, Rating, Notes, Price, CityID, UserID)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        new_id, _ = self.execute(sql, (name, is_sbb, max_dialog, rating, note, price, city_id, user_id))
        return Location(new_id, name, is_sbb, max_dialog, rating, note, price, city_id, user_id)

    def update_location(self, location: Location) -> None:
        sql = """
        UPDATE Locations
        SET Name = ?, IsSBB = ?, MaxDialog = ?, Rating = ?, Notes = ?, Price = ?, CityID = ?, UserID = ?
        WHERE LocationID = ?
        """
        self.execute(sql, (location.name, location.is_sbb, location.max_dialog, location.rating,
                          location.note, location.price, location.city_id, location.user_id, location.location_id))

    def delete_location(self, location_id: int) -> None:
        sql = "DELETE FROM Locations WHERE LocationID = ?"
        self.execute(sql, (location_id,))
