from __future__ import annotations
from datetime import date, datetime

class LocationLimit:
    def __init__(self,location_limit_id, location_limit_yearly, location_limit_monthly, location_limit_campaign, location_id, valid_from, user_id):
        self.__location_limit_id = location_limit_id
        self.__location_limit_yearly = location_limit_yearly
        self.__location_limit_monthly = location_limit_monthly
        self.__location_limit_campaign = location_limit_campaign
        self.__location_id = location_id
        self.__valid_from = valid_from
        self.__user_id = user_id

    def __repr__(self):
        return (
            f"Location Limit ID(id={self.__location_limit_id!r}, location limit yearly={self.__location_limit_yearly!r}, Location limit monthly={self.__location_limit_monthly!r}"
            f"Location Limit Campaign={self.__location_limit_campaign!r}), location ID={self.__location_id!r}, valid from={self.__valid_from!r}, user_id={self.__user_id!r}")


    @property
    def location_limit_id(self) -> int:
        return self.__location_limit_id

    @property
    def location_limit_yearly(self) -> int:
        return self.__location_limit_yearly

    @property
    def location_limit_monthly(self) -> int:
        return self.__location_limit_monthly

    @property
    def location_limit_campaign(self) -> int:
        return self.__location_limit_campaign

    @property
    def location_id(self) -> int:
        return self.__location_id

    @property
    def valid_from(self) -> date:
        return self.__valid_from

    @property
    def user_id(self) -> int:
        return self.__user_id

    @location_limit_yearly.setter
    def location_limit_yearly(self, location_limit_yearly):
        if not location_limit_yearly:
            raise ValueError("Location Limit yearly is required")
        if not isinstance(location_limit_yearly, int):
            raise TypeError("Location Limit yearly must be a Int")
        self.__location_limit_yearly = location_limit_yearly

    @location_limit_monthly.setter
    def location_limit_monthly(self, location_limit_monthly):
        if not location_limit_monthly:
            raise ValueError("Location Limit monthly is required")
        if not isinstance(location_limit_monthly, int):
            raise TypeError("Location Limit monthly must be a Int")
        self.__location_limit_monthly = location_limit_monthly

    @location_limit_campaign.setter
    def location_limit_campaign(self, location_limit_campaign):
        if not location_limit_campaign:
            raise ValueError("Location Limit campaign is required")
        if not isinstance(location_limit_campaign, int):
            raise TypeError("Location Limit campaign must be a Int")
        self.__location_limit_campaign = location_limit_campaign

    @location_id.setter
    def location_id(self, location_id):
        if not location_id:
            raise ValueError("Location ID is required")
        if not isinstance(location_id, int):
            raise TypeError("Location ID must be a Int")
        self.__location_id = location_id

    @valid_from.setter
    def valid_from(self, valid_from):
        if not valid_from:
            raise ValueError("Valid from is required")
        if not isinstance(valid_from, date):
            raise TypeError("Valid from must be a date")
        self.__valid_from = valid_from

    @user_id.setter
    def user_id(self, user_id):
        if not user_id:
            raise ValueError("User ID is required")
        if not isinstance(user_id, int):
            raise TypeError("User ID must be a Int")
        self.__user_id = user_id
