from __future__ import annotations
from datetime import date, datetime


class CityLimit:
    def __init__(self, city_limit_id, city_limit_yearly, city_limit_monthly, city_limit_campaign, city_limit_yearly_per_l, city_limit_monthly_per_l, city_limit_campaign_per_l, valid_from, unlimited, city_id):
        self.__city_limit_id = city_limit_id
        self.__city_limit_yearly = city_limit_yearly
        self.__city_limit_monthly = city_limit_monthly
        self.__city_limit_campaign = city_limit_campaign
        self.__city_limit_yearly_per_l = city_limit_yearly_per_l
        self.__city_limit_monthly_per_l = city_limit_monthly_per_l
        self.__city_limit_campaign_per_l = city_limit_campaign_per_l
        self.__valid_from = valid_from
        self.__unlimited = unlimited
        self.__city_id = city_id

    def __repr__(self):
        return (
            f"City Limit(id={self.__city_limit_id!r}, City Limit Yearly={self.__city_limit_yearly!r}, City Limit Monthly={self.__city_limit_monthly!r}"
            f"City Limit Campaign={self.__city_limit_campaign!r}), City Limit Yearly per Location={self.__city_limit_yearly_per_l!r}, City Limit Monthly per Location={self.__city_limit_monthly_per_l!r}, city Limit Campaign per Location={self.__city_limit_campaign_per_l!r}"
            f"Date valid from={self.__valid_from!r}, city ID={self.__city_id!r}")


    @property
    def city_limit_id(self):
        return self.__city_limit_id

    @property
    def city_limit_yearly(self):
        return self.__city_limit_yearly

    @property
    def city_limit_monthly(self):
        return self.__city_limit_monthly

    @property
    def city_limit_campaign(self):
        return self.__city_limit_campaign

    @property
    def city_limit_yearly_per_l(self):
        return self.__city_limit_yearly_per_l

    @property
    def city_limit_monthly_per_l(self):
        return self.__city_limit_monthly_per_l

    @property
    def city_limit_campaign_per_l(self):
        return self.__city_limit_campaign_per_l

    @property
    def valid_from(self):
        return self.__valid_from

    @property
    def unlimited(self):
        return self.__unlimited

    @property
    def city_id(self):
        return self.__city_id

    @city_limit_yearly.setter
    def city_limit_yearly(self, city_limit_yearly):
        if not city_limit_yearly:
            raise ValueError("City limit Yearly is required")
        if not isinstance(city_limit_yearly, int):
            raise TypeError("City Limit Yearly must be a Int")
        self.__city_limit_yearly = city_limit_yearly

    @city_limit_monthly.setter
    def city_limit_monthly(self, city_limit_monthly):
        if not city_limit_monthly:
            raise ValueError("City limit Monthly is required")
        if not isinstance(city_limit_monthly, int):
            raise TypeError("City Limit Monthly must be a Int")
        self.__city_limit_monthly = city_limit_monthly

    @city_limit_campaign.setter
    def city_limit_campaign(self, city_limit_campaign):
        if not city_limit_campaign:
            raise ValueError("City limit Campaign is required")
        if not isinstance(city_limit_campaign, int):
            raise TypeError("City Limit Campaign must be a Int")
        self.__city_limit_campaign = city_limit_campaign

    @city_limit_yearly_per_l.setter
    def city_limit_yearly_per_l(self, city_limit_yearly_per_l):
        if not city_limit_yearly_per_l:
            raise ValueError("City limit Yearly per Location is required")
        if not isinstance(city_limit_yearly_per_l, int):
            raise TypeError("City Limit Yearly per Location must be a Int")
        self.__city_limit_yearly_per_l = city_limit_yearly_per_l

    @city_limit_monthly_per_l.setter
    def city_limit_monthly_per_l(self, city_limit_monthly_per_l):
        if not city_limit_monthly_per_l:
            raise ValueError("City Limit Monthly per Location is required")
        if not isinstance(city_limit_monthly_per_l, int):
            raise TypeError("City Limit Monthly per Location must be a Int")
        self.__city_limit_monthly_per_l = city_limit_monthly_per_l

    @city_limit_campaign_per_l.setter
    def city_limit_campaign_per_l(self, city_limit_campaign_per_l):
        if not city_limit_campaign_per_l:
            raise ValueError("City Limit Campaign per Location is required")
        if not isinstance(city_limit_campaign_per_l, int):
            raise TypeError("City Limit Campaign per Location must be a Int")
        self.__city_limit_campaign_per_l = city_limit_campaign_per_l

    @valid_from.setter
    def valid_from(self, valid_from):
        if not valid_from:
            raise ValueError("Date Valid From is required")
        if not isinstance(valid_from, date):
            raise TypeError("Date of event must be a date")
        self.__valid_from = valid_from

    @unlimited.setter
    def unlimited(self, unlimited):
        if not isinstance(unlimited, bool):
            raise TypeError("Unlimited must be a Bool")
        self.__unlimited = unlimited

    @city_id.setter
    def city_id(self, city_id):
        if not city_id:
            raise ValueError("City ID is required")
        if not isinstance(city_id, int):
            raise TypeError("City ID must be a Int")
        self.__city_id = city_id
