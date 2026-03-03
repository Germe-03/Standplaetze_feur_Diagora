from __future__ import annotations
from datetime import date, datetime

class Booking:
    def __init__(self, booking_id, date_of_booking, date_of_event, date_of_last_update, price, confirmed, location_id, cancelled, campaign_id, user_id):
        self.__booking_id = booking_id
        self.__date_of_booking = date_of_booking
        self.__date_of_event = date_of_event
        self.__date_of_last_update = date_of_last_update
        self.__price = price
        self.__confirmed = confirmed
        self.__location_id = location_id
        self.__cancelled = cancelled
        self.__campaign_id = campaign_id
        self.__user_id = user_id

    def __repr__(self):
        return (
            f"Booking(id={self.__booking_id!r}, date_of_booking={self.__date_of_booking!r}, "
            f"date_of_event={self.__date_of_event!r}, date_of_last_update={self.__date_of_last_update!r}, "
            f"price={self.__price!r}, confirmed={self.__confirmed!r}, location_id={self.__location_id!r}, "
            f"cancelled={self.__cancelled!r}, campaign_id={self.__campaign_id!r}, user_id={self.__user_id!r})"
        )

    @property
    def booking_id(self):
        return self.__booking_id

    @property
    def date_of_booking(self):
        return self.__date_of_booking

    @date_of_booking.setter
    def date_of_booking(self, date_of_booking: date | datetime | str):
        if not date_of_booking:
            raise ValueError("Date of booking is required")
        if not isinstance(date_of_booking, date):
            raise TypeError("Date of booking must be a string")
        self.__date_of_booking = date_of_booking

    @property
    def date_of_event(self):
        return self.__date_of_event

    @date_of_event.setter
    def date_of_event(self, date_of_event: date | datetime | str):
        if not date_of_event:
            raise ValueError("Date of event is required")
        if not isinstance(date_of_event, date):
            raise TypeError("Date of event must be a string")
        self.__date_of_event = date_of_event

    @property
    def date_of_last_update(self):
        return self.__date_of_last_update

    @date_of_last_update.setter
    def date_of_last_update(self, date_of_last_update: date | datetime | str):
        if not date_of_last_update:
            raise ValueError("Date of last update is required")
        if not isinstance(date_of_last_update, date):
            raise TypeError("Date of last update must be a string")
        self.__date_of_last_update = date_of_last_update

    @property
    def price(self):
        return self.__price

    @price.setter
    def price(self, price):
        if not isinstance(price, (int, float)):
            raise TypeError("Price must be a float")
        if price is None:
            raise ValueError("Price is required")
        self.__price = float(price)

    @property
    def confirmed(self):
        return self.__confirmed

    @confirmed.setter
    def confirmed(self, confirmed):
        if not isinstance(confirmed, bool):
            raise TypeError("Confirmed must be a bool")
        self.__confirmed = confirmed

    @property
    def location_id(self):
        return self.__location_id

    @location_id.setter
    def location_id(self, location_id):
        if not isinstance(location_id, int):
            raise TypeError("Location ID must be a int")
        if not location_id:
            raise ValueError("Location ID is required")
        self.__location_id = location_id

    @property
    def cancelled(self):
        return self.__cancelled

    @cancelled.setter
    def cancelled(self, cancelled):
        if not isinstance(cancelled, bool):
            raise TypeError("Cancelled must be a bool")
        self.__cancelled = cancelled

    @property
    def campaign_id(self):
        return self.__campaign_id

    @campaign_id.setter
    def campaign_id(self, campaign_id):
        if not isinstance(campaign_id, int):
            raise TypeError("Campaign ID must be a int")
        if not campaign_id:
            raise ValueError("Campaign ID is required")
        self.__campaign_id = campaign_id

    @property
    def user_id(self):
        return self.__user_id

    @user_id.setter
    def user_id(self, user_id):
        if not isinstance(user_id, int):
            raise TypeError("User ID must be a int")
        if not user_id:
            raise ValueError("User ID is required")
        self.__user_id = user_id

