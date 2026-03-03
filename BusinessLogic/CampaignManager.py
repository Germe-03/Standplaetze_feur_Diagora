from datetime import date
from typing import List, Optional, Dict

from DataAccess.CampaignDataAccess import CampaignDataAccess
from DataAccess.UserDataAccess import UserDataAccess
from Model.Campaign import Campaign


class CampaignManager:
    def __init__(self, db_path: str = None):
        self.campaign_dao = CampaignDataAccess(db_path)
        self.user_dao = UserDataAccess(db_path)

    def create_campaign(self, name: str, year: int, budget: float, user_id: int) -> Campaign:
        """
        Erstellt eine neue Kampagne mit Validierung der Geschäftsregeln
        """
        # Geschäftsregeln validieren
        self._validate_campaign_data(name, year, budget, user_id)

        # Prüfen ob User existiert
        user = self.user_dao.get_user_by_id(user_id)
        if not user:
            raise ValueError("Benutzer existiert nicht")

        # Prüfen ob Kampagne mit gleichem Namen/Jahr/User bereits existiert
        campaigns_with_same_name = self.campaign_dao.get_campaign_by_name(name.strip())
        duplicate_campaign = next(
            (
                c
                for c in campaigns_with_same_name
                if c.year == year and c.user_id == user_id
            ),
            None,
        )
        if duplicate_campaign:
            raise ValueError("Diese Kampagne existiert für den Benutzer bereits")

        # Kampagne erstellen
        return self.campaign_dao.insert_campaign(name.strip(), year, float(budget), user_id)

    def get_campaign_by_id(self, campaign_id: int) -> Optional[Campaign]:
        """
        Holt eine Kampagne nach ID
        """
        if not campaign_id or campaign_id <= 0:
            raise ValueError("Ungültige Kampagnen-ID")

        return self.campaign_dao.get_campaign_by_id(campaign_id)

    def get_campaigns_by_name(self, name: str) -> List[Campaign]:
        """
        Holt alle Kampagnen mit einem bestimmten Namen
        """
        if not name or not name.strip():
            raise ValueError("Kampagnenname muss angegeben werden")

        return self.campaign_dao.get_campaign_by_name(name.strip())

    def get_campaigns_by_user(self, user_id: int) -> List[Campaign]:
        """
        Holt alle Kampagnen eines Benutzers
        """
        if not user_id or user_id <= 0:
            raise ValueError("Ungültige User-ID")

        return self.campaign_dao.get_campaign_by_user_id(user_id)

    def get_campaigns_by_year(self, year: int) -> List[Campaign]:
        """
        Holt alle Kampagnen eines Jahres
        """
        current_year = date.today().year
        if not isinstance(year, int):
            raise ValueError("Jahr muss eine ganze Zahl sein")
        if year < 1900 or year > current_year + 10:
            raise ValueError("Ungültiges Kampagnenjahr")

        return self.campaign_dao.get_campaign_by_year(year)

    def update_campaign(self, campaign: Campaign) -> None:
        """
        Aktualisiert eine bestehende Kampagne
        """
        if not campaign or not campaign.campaign_id:
            raise ValueError("Ungültige Kampagne")

        # Prüfen ob Kampagne existiert
        existing_campaign = self.campaign_dao.get_campaign_by_id(campaign.campaign_id)
        if not existing_campaign:
            raise ValueError("Kampagne existiert nicht")

        # Geschäftsregeln validieren
        self._validate_campaign_data(campaign.name, campaign.year, campaign.budget, campaign.user_id)

        # Prüfen ob User existiert
        user = self.user_dao.get_user_by_id(campaign.user_id)
        if not user:
            raise ValueError("Benutzer existiert nicht")

        # Prüfen ob Name/Jahr/User bereits von anderer Kampagne belegt ist
        campaigns_with_same_name = self.campaign_dao.get_campaign_by_name(campaign.name.strip())
        duplicate_campaign = next(
            (
                c
                for c in campaigns_with_same_name
                if c.campaign_id != campaign.campaign_id
                and c.year == campaign.year
                and c.user_id == campaign.user_id
            ),
            None,
        )
        if duplicate_campaign:
            raise ValueError("Eine andere Kampagne mit gleichem Namen, Jahr und Benutzer existiert bereits")

        # Kampagne aktualisieren
        self.campaign_dao.update_campaign(campaign)

    def delete_campaign(self, campaign_id: int) -> None:
        """
        Löscht eine Kampagne
        """
        if not campaign_id or campaign_id <= 0:
            raise ValueError("Ungültige Kampagnen-ID")

        # Prüfen ob Kampagne existiert
        existing_campaign = self.campaign_dao.get_campaign_by_id(campaign_id)
        if not existing_campaign:
            raise ValueError("Kampagne existiert nicht")

        # Kampagne löschen
        self.campaign_dao.delete_campaign(campaign_id)

    def validate_campaign_exists(self, campaign_id: int) -> bool:
        """
        Prüft ob eine Kampagne existiert
        """
        if not campaign_id or campaign_id <= 0:
            return False

        campaign = self.campaign_dao.get_campaign_by_id(campaign_id)
        return campaign is not None

    def get_campaign_statistics(self, year: int = None) -> Dict:
        """
        Gibt Statistiken über Kampagnen zurück
        """
        if year is not None:
            campaigns = self.get_campaigns_by_year(year)
        else:
            current_year = date.today().year
            campaigns = self.get_campaigns_by_year(current_year)

        if not campaigns:
            return {
                "total_campaigns": 0,
                "total_budget": 0.0,
                "average_budget": 0.0,
                "max_budget": 0.0,
                "min_budget": 0.0,
            }

        budgets = [float(c.budget) for c in campaigns]
        total_budget = sum(budgets)
        average_budget = total_budget / len(campaigns)

        return {
            "total_campaigns": len(campaigns),
            "total_budget": round(total_budget, 2),
            "average_budget": round(average_budget, 2),
            "max_budget": round(max(budgets), 2),
            "min_budget": round(min(budgets), 2),
        }

    def _validate_campaign_data(self, name: str, year: int, budget: float, user_id: int) -> None:
        """
        Validiert Kampagnendaten nach Geschäftsregeln
        """
        current_year = date.today().year

        # Pflichtfelder prüfen
        if not name or not name.strip():
            raise ValueError("Kampagnenname ist ein Pflichtfeld")

        if not isinstance(year, int):
            raise ValueError("Jahr muss eine ganze Zahl sein")
        if year < 1900 or year > current_year + 10:
            raise ValueError("Ungültiges Kampagnenjahr")

        if budget is None:
            raise ValueError("Budget ist ein Pflichtfeld")
        if not isinstance(budget, (int, float)):
            raise ValueError("Budget muss eine Zahl sein")
        if float(budget) < 0:
            raise ValueError("Budget darf nicht negativ sein")

        if not user_id or user_id <= 0:
            raise ValueError("Benutzer ist ein Pflichtfeld")

        # Längenvalidierung
        if len(name.strip()) < 2:
            raise ValueError("Kampagnenname muss mindestens 2 Zeichen lang sein")
