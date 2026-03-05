from DataAccess.BaseDataAccess import BaseDataAccess
from Model.Campaign import Campaign


class CampaignDataAccess(BaseDataAccess):
    def __init__(self, db_path: str = None):
        super().__init__(db_path)
        self._ensure_is_active_column()

    def _ensure_is_active_column(self) -> None:
        rows = self.fetchall("PRAGMA table_info(Campaign)")
        columns = {str(row[1]).lower() for row in rows}
        if "isactive" in columns:
            return
        self.execute("ALTER TABLE Campaign ADD COLUMN IsActive INTEGER NOT NULL DEFAULT 1")
        self.execute("UPDATE Campaign SET IsActive = 1 WHERE IsActive IS NULL")

    def get_campaign_by_id(self, campaign_id: int) -> Campaign | None:
        sql = """
        select CampaignID, Name, Year, Budget, UserID, IsActive
        from Campaign
        where CampaignID = ?   
        """
        row = self.fetchone(sql, (campaign_id,))
        if row:
            return Campaign(*row)
        return None

    def get_campaign_by_name(self, name: str) -> list[Campaign]:
        sql = """
        select CampaignID, Name, Year, Budget, UserID, IsActive
        from Campaign
        where Name = ?
        """
        rows = self.fetchall(sql, (name,))
        return [Campaign(*row) for row in rows]

    def get_campaign_by_user_id(self, user_id: int) -> list[Campaign]:
        sql = """
        select CampaignID, Name, Year, Budget, UserID, IsActive
        from Campaign
        where UserID = ?
        """
        rows = self.fetchall(sql, (user_id,))
        return [Campaign(*row) for row in rows]

    def get_campaign_by_year(self, year: int) -> list[Campaign]:
        sql = """
        select CampaignID, Name, Year, Budget, UserID, IsActive
        from Campaign
        where Year = ?
        """
        rows = self.fetchall(sql, (year,))
        return [Campaign(*row) for row in rows]

    def get_all_campaigns(self) -> list[Campaign]:
        sql = """
        select CampaignID, Name, Year, Budget, UserID, IsActive
        from Campaign
        """
        rows = self.fetchall(sql)
        return [Campaign(*row) for row in rows]

    def insert_campaign(self, name: str, year: int, budget: float, user_id: int, is_active: bool = True) -> Campaign:
        sql = """
        INSERT INTO Campaign (Name, Year, Budget, UserID, IsActive)
        VALUES (?, ?, ?, ?, ?)
        """
        new_id, _ = self.execute(sql, (name, year, budget, user_id, 1 if is_active else 0))
        return Campaign(new_id, name, year, budget, user_id, is_active)

    def update_campaign(self, campaign: Campaign) -> None:
        sql = """
        UPDATE Campaign
        SET Name = ?, Year = ?, Budget = ?, UserID = ?, IsActive = ?
        WHERE CampaignID = ?
        """
        self.execute(sql, (campaign.name, campaign.year, campaign.budget, campaign.user_id, 1 if campaign.is_active else 0, campaign.campaign_id))

    def delete_campaign(self, campaign_id: int) -> None:
        sql = "DELETE FROM Campaign WHERE CampaignID = ?"
        self.execute(sql, (campaign_id,))

    
