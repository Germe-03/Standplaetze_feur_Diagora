import os

from DataAccess.BaseDataAccess import BaseDataAccess
from Model.Booking import Booking
from Model.Location import Location
from Model.Campaign import Campaign
from Model.User import User


class BookingDataAccess(BaseDataAccess):
    def __init__(self, db_path: str = None):
        super().__init__(db_path)

    def get_booking_by_id(self, booking_id: int) -> Booking | None:
        sql = """
        select BookingID, DateOfBooking, DateOfEvent, DateOfLastUpdate,
            Price, Confirmed, LocationID, CampaignID, UserID
        from Bookings
        where BookingID = ?    
        """
        row = self.fetchone(sql, (booking_id,))
        if row:
            return Booking(*row)
        return None

    def get_bookings_by_date_of_booking(self, start_us_date: str, end_us_date: str) -> list[Booking]:
        sql = """
        select BookingID, DateOfBooking, DateOfEvent, DateOfLastUpdate,
            Price, Confirmed, LocationID, CampaignID, UserID
        from Bookings
        where DateOfBooking between ? and ?
        """
        rows = self.fetchall(sql, (start_us_date, end_us_date))
        return [Booking(*row) for row in rows]

    def get_bookings_by_date_of_event(self, start_us_date: str, end_us_date: str) -> list[Booking]:
        sql = """
        select BookingID, DateOfBooking, DateOfEvent, DateOfLastUpdate,
            Price, Confirmed, LocationID, CampaignID, UserID
        from Bookings
        where DateOfEvent between ? and ?
        """
        rows = self.fetchall(sql, (start_us_date, end_us_date))
        return [Booking(*row) for row in rows]

    def get_bookings_by_date_of_last_update(self, start_us_date: str, end_us_date: str) -> list[Booking]:
        sql = """
        select BookingID, DateOfBooking, DateOfEvent, DateOfLastUpdate,
            Price, Confirmed, LocationID, CampaignID, UserID
        from Bookings
        where DateOfLastUpdate between ? and ?
        """
        rows = self.fetchall(sql, (start_us_date, end_us_date))
        return [Booking(*row) for row in rows]

    def get_bookings_by_price(self, min_price: float, max_price: float) -> list[Booking]:
        sql = """
        select BookingID, DateOfBooking, DateOfEvent, DateOfLastUpdate,
            Price, Confirmed, LocationID, CampaignID, UserID
        from Bookings
        where Price between ? and ?
        """
        rows = self.fetchall(sql, (min_price, max_price))
        return [Booking(*row) for row in rows]

    def get_bookings_by_campaign_id(self, campaign_id: int) -> list[Booking]:
        sql = """
        select BookingID, DateOfBooking, DateOfEvent, DateOfLastUpdate,
            Price, Confirmed, LocationID, CampaignID, UserID
        from Bookings
        where CampaignID = ?
        """
        rows = self.fetchall(sql, (campaign_id,))
        return [Booking(*row) for row in rows]

    def get_bookings_by_location_id(self, location_id: int) -> list[Booking]:
        sql = """
        select BookingID, DateOfBooking, DateOfEvent, DateOfLastUpdate,
            Price, Confirmed, LocationID, CampaignID, UserID
        from Bookings
        where LocationID = ?
        """
        rows = self.fetchall(sql, (location_id,))
        return [Booking(*row) for row in rows]

    def get_bookings_by_user_id(self, user_id: int) -> list[Booking]:
        sql = """
        select BookingID, DateOfBooking, DateOfEvent, DateOfLastUpdate,
            Price, Confirmed, LocationID, CampaignID, UserID
        from Bookings
        where UserID = ?
        """
        rows = self.fetchall(sql, (user_id,))
        return [Booking(*row) for row in rows]
