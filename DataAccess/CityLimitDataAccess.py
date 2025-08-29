from DataAccess.BaseDataAccess import BaseDataAccess
from Model.CityLimit import CityLimit
from datetime import date


class CityLimitDataAccess(BaseDataAccess):
    def __init__(self, db_path: str = None):
        super().__init__(db_path)

    def get_city_limit_by_id(self, city_limit_id: int) -> CityLimit | None:
        sql = """
        select CityLimitID, CityLimitYearly, CityLimitMonthly, CityLimitCampaign, 
               CityLimitYearlyPerL, CityLimitMonthlyPerL, CityLimitCampaignPerL, 
               ValidFrom, Unlimited, CityID
        from CityLimits
        where CityLimitID = ?   
        """
        row = self.fetchone(sql, (city_limit_id,))
        if row:
            return CityLimit(*row)
        return None

    def get_city_limit_by_city_name(self, city_name: str) -> list[CityLimit]:
        sql = """
        select cl.CityLimitID, cl.CityLimitYearly, cl.CityLimitMonthly, cl.CityLimitCampaign, 
               cl.CityLimitYearlyPerL, cl.CityLimitMonthlyPerL, cl.CityLimitCampaignPerL, 
               cl.ValidFrom, cl.Unlimited, cl.CityID
        from CityLimits cl
        join Cities c on c.CityID = cl.CityID
        where c.Name = ?
        """
        rows = self.fetchall(sql, (city_name,))
        return [CityLimit(*row) for row in rows]

    def get_city_limits_by_unlimited(self, unlimited: bool) -> list[CityLimit]:
        sql = """
        select CityLimitID, CityLimitYearly, CityLimitMonthly, CityLimitCampaign, 
               CityLimitYearlyPerL, CityLimitMonthlyPerL, CityLimitCampaignPerL, 
               ValidFrom, Unlimited, CityID
        from CityLimits
        where Unlimited = ?
        """
        rows = self.fetchall(sql, (unlimited,))
        return [CityLimit(*row) for row in rows]

    def insert_city_limit(self, city_limit_yearly: int, city_limit_monthly: int, city_limit_campaign: int,
                         city_limit_yearly_per_l: int, city_limit_monthly_per_l: int, city_limit_campaign_per_l: int,
                         valid_from: date, unlimited: bool, city_id: int) -> CityLimit:
        sql = """
        INSERT INTO CityLimits (CityLimitYearly, CityLimitMonthly, CityLimitCampaign, 
                               CityLimitYearlyPerL, CityLimitMonthlyPerL, CityLimitCampaignPerL, 
                               ValidFrom, Unlimited, CityID)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        new_id, _ = self.execute(sql, (city_limit_yearly, city_limit_monthly, city_limit_campaign,
                                      city_limit_yearly_per_l, city_limit_monthly_per_l, city_limit_campaign_per_l,
                                      valid_from, unlimited, city_id))
        return CityLimit(new_id, city_limit_yearly, city_limit_monthly, city_limit_campaign,
                        city_limit_yearly_per_l, city_limit_monthly_per_l, city_limit_campaign_per_l,
                        valid_from, unlimited, city_id)

    def update_city_limit(self, city_limit: CityLimit) -> None:
        sql = """
        UPDATE CityLimits
        SET CityLimitYearly = ?, CityLimitMonthly = ?, CityLimitCampaign = ?, 
            CityLimitYearlyPerL = ?, CityLimitMonthlyPerL = ?, CityLimitCampaignPerL = ?, 
            ValidFrom = ?, Unlimited = ?, CityID = ?
        WHERE CityLimitID = ?
        """
        self.execute(sql, (city_limit.city_limit_yearly, city_limit.city_limit_monthly, city_limit.city_limit_campaign,
                          city_limit.city_limit_yearly_per_l, city_limit.city_limit_monthly_per_l, city_limit.city_limit_campaign_per_l,
                          city_limit.valid_from, city_limit.unlimited, city_limit.city_id, city_limit.city_limit_id))

    def delete_city_limit(self, city_limit_id: int) -> None:
        sql = "DELETE FROM CityLimits WHERE CityLimitID = ?"
        self.execute(sql, (city_limit_id,))
