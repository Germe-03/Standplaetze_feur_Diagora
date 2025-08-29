from DataAccess.BaseDataAccess import BaseDataAccess
from Model.Campaign import Campaign


class CampaignDataAccess(BaseDataAccess):
    def __init__(self, db_path: str = None):
        super().__init__(db_path)

    def get_campaign_by_id(self, campaign_id: int) -> Campaign | None:
        sql = """
        select CampaignID, Name, Year, Budget, UserID
        from Campaign
        where CampaignID = ?   
        """
        row = self.fetchone(sql, (campaign_id,))
        if row:
            return Campaign(*row)
        return None

    def get_campaign_by_name(self, name: str) -> list[Campaign]:
        sql = """
        select CampaignID, Name, Year, Budget, UserID
        from Campaign
        where Name = ?
        """
        rows = self.fetchall(sql, (name,))
        return [Campaign(*row) for row in rows]

    def get_campaign_by_user_id(self, user_id: int) -> list[Campaign]:
        sql = """
        select CampaignID, Name, Year, Budget, UserID
        from Campaign
        where UserID = ?
        """
        rows = self.fetchall(sql, (user_id,))
        return [Campaign(*row) for row in rows]

    def get_campaign_by_year(self, year: int) -> list[Campaign]:
        sql = """
        select CampaignID, Name, Year, Budget, UserID
        from Campaign
        where Year = ?
        """
        rows = self.fetchall(sql, (year,))
        return [Campaign(*row) for row in rows]

    def insert_campaign(self, name: str, year: int, budget: float, user_id: int) -> Campaign:
        sql = """
        INSERT INTO Campaign (Name, Year, Budget, UserID)
        VALUES (?, ?, ?, ?)
        """
        new_id, _ = self.execute(sql, (name, year, budget, user_id))
        return Campaign(new_id, name, year, budget, user_id)

    def update_campaign(self, campaign: Campaign) -> None:
        sql = """
        UPDATE Campaign
        SET Name = ?, Year = ?, Budget = ?, UserID = ?
        WHERE CampaignID = ?
        """
        self.execute(sql, (campaign.name, campaign.year, campaign.budget, campaign.user_id, campaign.campaign_id))

    def delete_campaign(self, campaign_id: int) -> None:
        sql = "DELETE FROM Campaign WHERE CampaignID = ?"
        self.execute(sql, (campaign_id,))

    