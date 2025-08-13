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
            return (f"Booking(id={self.__booking_id!r}, Date of Booking={self.__date_of_booking!r}, Date Of last Event={self.__date_of_event!r}"
                    f"Date of Last Update={self.__date_of_last_update!r}), price={self.__price!r}, confirmed={self.__confirmed!r}, location_id={self.__Location_id!r}"
                    f"cancelled={self.__cancelled!r}, campaign ID={self.__campaign_id!r}, user ID={self.__user_id!r}")

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

    @property
    def date_of_event(self):
        return self.__date_of_event

    @date_of_event.setter
    def date_of_event(self, date_of_event: date | datetime | str):
        if not date_of_event:
            raise ValueError("Date of event is required")
        if not isinstance(date_of_event, date):
            raise TypeError("Date of event must be a string")

    @property
    def date_of_last_update(self):
        return self.__date_of_last_update

    @date_of_last_update.setter
    def date_of_last_update(self, date_of_last_update: date | datetime | str):
        if not date_of_last_update:
            raise ValueError("Date of last update is required")
        if not isinstance(date_of_last_update, date):
            raise TypeError("Date of last update must be a string")

    @property
    def price(self):
        return self.__price

    @price.setter
    def price(self, price):
        if not isinstance(price, float):
            raise TypeError("Price must be a float")
        if not price:
            raise ValueError("Price is required")

    @property
    def confirmed(self):
        return self.__confirmed

    @confirmed.setter
    def confirmed(self, confirmed):
        if not isinstance(confirmed, bool):
            raise TypeError("Confirmed must be a bool")
        if not confirmed:
            raise ValueError("Confirmed is required")

    @property
    def location_id(self):
        return self.__location_id

    @location_id.setter
    def location_id(self, location_id):
        if not isinstance(location_id, int):
            raise TypeError("Location ID must be a int")
        if not location_id:
            raise ValueError("Location ID is required")

    @property
    def cancelled(self, cancelled):
        return self.__cancelled

    @cancelled.setter
    def cancelled(self, cancelled):
        if not isinstance(cancelled, bool):
            raise TypeError("Cancelled must be a bool")
        if not cancelled:
            raise ValueError("Cancelled is required")

    @property
    def campaign_id(self, campaign_id):
        return self.__campaign_id

    @campaign_id.setter
    def campaign_id(self, campaign_id):
        if not isinstance(campaign_id, int):
            raise TypeError("Campaign ID must be a int")
        if not campaign_id:
            raise ValueError("Campaign ID is required")

    @property
    def user_id(self):
        return self.__user_id

    @user_id.setter
    def user_id(self, user_id):
        if not isinstance(user_id, int):
            raise TypeError("User ID must be a int")
        if not user_id:
            raise ValueError("User ID is required")

