from DataAccess.BaseDataAccess import BaseDataAccess
from Model.LocationLimit import LocationLimit
from datetime import date


class LocationLimitsDataAccess(BaseDataAccess):
    def __init__(self, db_path: str = None):
        super().__init__(db_path)

    def get_location_limit_by_id(self, location_limit_id: int) -> LocationLimit | None:
        sql = """
        select LocationLimitID, LocationLimitYearly, LocationLimitMonthly, LocationLimitCampaign, 
               LocationID, ValidFrom, UserID
        from LocationLimits
        where LocationLimitID = ?   
        """
        row = self.fetchone(sql, (location_limit_id,))
        if row:
            return LocationLimit(*row)
        return None

    def get_location_limit_by_location_name(self, location_name: str) -> list[LocationLimit]:
        sql = """
        select ll.LocationLimitID, ll.LocationLimitYearly, ll.LocationLimitMonthly, ll.LocationLimitCampaign, 
               ll.LocationID, ll.ValidFrom, ll.UserID
        from LocationLimits ll
        join Locations l on l.LocationID = ll.LocationID
        where l.Name = ?
        """
        rows = self.fetchall(sql, (location_name,))
        return [LocationLimit(*row) for row in rows]

    def get_location_limits_by_user_id(self, user_id: int) -> list[LocationLimit]:
        sql = """
        select LocationLimitID, LocationLimitYearly, LocationLimitMonthly, LocationLimitCampaign, 
               LocationID, ValidFrom, UserID
        from LocationLimits
        where UserID = ?
        """
        rows = self.fetchall(sql, (user_id,))
        return [LocationLimit(*row) for row in rows]

    def get_location_limits_by_location_id(self, location_id: int) -> list[LocationLimit]:
        sql = """
        select LocationLimitID, LocationLimitYearly, LocationLimitMonthly, LocationLimitCampaign, 
               LocationID, ValidFrom, UserID
        from LocationLimits
        where LocationID = ?
        """
        rows = self.fetchall(sql, (location_id,))
        return [LocationLimit(*row) for row in rows]

    def get_location_limits_by_valid_from(self, valid_from: date) -> list[LocationLimit]:
        sql = """
        select LocationLimitID, LocationLimitYearly, LocationLimitMonthly, LocationLimitCampaign, 
               LocationID, ValidFrom, UserID
        from LocationLimits
        where ValidFrom = ?
        """
        rows = self.fetchall(sql, (valid_from,))
        return [LocationLimit(*row) for row in rows]

    def insert_location_limit(self, location_limit_yearly: int, location_limit_monthly: int, 
                            location_limit_campaign: int, location_id: int, valid_from: date, user_id: int) -> LocationLimit:
        sql = """
        INSERT INTO LocationLimits (LocationLimitYearly, LocationLimitMonthly, LocationLimitCampaign, 
                                   LocationID, ValidFrom, UserID)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        new_id, _ = self.execute(sql, (location_limit_yearly, location_limit_monthly, location_limit_campaign,
                                      location_id, valid_from, user_id))
        return LocationLimit(new_id, location_limit_yearly, location_limit_monthly, location_limit_campaign,
                           location_id, valid_from, user_id)

    def update_location_limit(self, location_limit: LocationLimit) -> None:
        sql = """
        UPDATE LocationLimits
        SET LocationLimitYearly = ?, LocationLimitMonthly = ?, LocationLimitCampaign = ?, 
            LocationID = ?, ValidFrom = ?, UserID = ?
        WHERE LocationLimitID = ?
        """
        self.execute(sql, (location_limit.location_limit_yearly, location_limit.location_limit_monthly, 
                          location_limit.location_limit_campaign, location_limit.location_id,
                          location_limit.valid_from, location_limit.user_id, location_limit.location_limit_id))

    def delete_location_limit(self, location_limit_id: int) -> None:
        sql = "DELETE FROM LocationLimits WHERE LocationLimitID = ?"
        self.execute(sql, (location_limit_id,))