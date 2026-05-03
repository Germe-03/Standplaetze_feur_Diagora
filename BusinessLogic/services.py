from __future__ import annotations

from datetime import date
from typing import List, Optional

from BusinessLogic.ports import (
    BookingRepository,
    CampaignRepository,
    ContactRepository,
    LocationRepository,
    UserRepository,
)
from Model.entities import Booking, Campaign, ContactInfo, Location, User


class UserService:
    def __init__(self, user_repo: UserRepository, contact_repo: ContactRepository) -> None:
        self._user_repo = user_repo
        self._contact_repo = contact_repo

    def create_user(self, name: str, email: str, phone: Optional[str] = None, address: Optional[str] = None) -> User:
        if not name or not name.strip():
            raise ValueError("Name ist erforderlich")
        if not email or "@" not in email:
            raise ValueError("Ungueltige E-Mail")

        user = self._user_repo.add(User(id=None, name=name.strip(), email=email.strip()))
        if phone or address:
            self._contact_repo.add(
                ContactInfo(id=None, user_id=user.id, phone=phone, address=address)
            )
        return user

    def list_users(self) -> List[User]:
        return self._user_repo.list()


class LocationService:
    def __init__(self, location_repo: LocationRepository) -> None:
        self._location_repo = location_repo

    def create_location(self, name: str, city: str, price: float) -> Location:
        if not name or not name.strip():
            raise ValueError("Name ist erforderlich")
        if not city or not city.strip():
            raise ValueError("Stadt ist erforderlich")
        if price is None or price < 0:
            raise ValueError("Preis muss >= 0 sein")

        return self._location_repo.add(
            Location(id=None, name=name.strip(), city=city.strip(), price=float(price))
        )

    def list_locations(self) -> List[Location]:
        return self._location_repo.list()


class CampaignService:
    def __init__(self, campaign_repo: CampaignRepository, user_repo: UserRepository) -> None:
        self._campaign_repo = campaign_repo
        self._user_repo = user_repo

    def create_campaign(self, name: str, year: int, budget: float, owner_id: int) -> Campaign:
        if not name or not name.strip():
            raise ValueError("Name ist erforderlich")
        if year < 2000 or year > 2100:
            raise ValueError("Jahr ist ungueltig")
        if budget is None or budget < 0:
            raise ValueError("Budget muss >= 0 sein")

        if not self._user_repo.get(owner_id):
            raise ValueError("Owner existiert nicht")

        return self._campaign_repo.add(
            Campaign(id=None, name=name.strip(), year=int(year), budget=float(budget), owner_id=owner_id)
        )

    def list_campaigns(self) -> List[Campaign]:
        return self._campaign_repo.list()


class BookingService:
    ALLOWED_STATUS = {"open", "confirmed", "cancelled"}

    def __init__(
        self,
        booking_repo: BookingRepository,
        location_repo: LocationRepository,
        campaign_repo: CampaignRepository,
        user_repo: UserRepository,
    ) -> None:
        self._booking_repo = booking_repo
        self._location_repo = location_repo
        self._campaign_repo = campaign_repo
        self._user_repo = user_repo

    def create_booking(
        self,
        event_date: date,
        price: float,
        status: str,
        location_id: int,
        campaign_id: int,
        user_id: int,
    ) -> Booking:
        if event_date < date.today():
            raise ValueError("Datum liegt in der Vergangenheit")
        if price is None or price < 0:
            raise ValueError("Preis muss >= 0 sein")
        if status not in self.ALLOWED_STATUS:
            raise ValueError("Status ungueltig")

        if not self._location_repo.get(location_id):
            raise ValueError("Standplatz existiert nicht")
        if not self._campaign_repo.get(campaign_id):
            raise ValueError("Kampagne existiert nicht")
        if not self._user_repo.get(user_id):
            raise ValueError("Benutzer existiert nicht")

        conflicts = self._booking_repo.list_by_location_date(location_id, event_date)
        active_conflicts = [item for item in conflicts if item.status != "cancelled"]
        if active_conflicts:
            raise ValueError("Standplatz ist bereits gebucht")

        return self._booking_repo.add(
            Booking(
                id=None,
                event_date=event_date,
                price=float(price),
                status=status,
                location_id=location_id,
                campaign_id=campaign_id,
                user_id=user_id,
            )
        )

    def list_bookings(self) -> List[Booking]:
        return self._booking_repo.list()
