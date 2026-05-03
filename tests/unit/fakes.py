from __future__ import annotations

from dataclasses import replace
from datetime import date
from typing import Dict, List, Optional

from Model.entities import Booking, Campaign, ContactInfo, Location, User


class InMemoryUserRepo:
    def __init__(self) -> None:
        self._items: Dict[int, User] = {}
        self._next_id = 1

    def add(self, user: User) -> User:
        user_id = self._next_id
        self._next_id += 1
        created = replace(user, id=user_id)
        self._items[user_id] = created
        return created

    def get(self, user_id: int) -> Optional[User]:
        return self._items.get(user_id)

    def list(self) -> List[User]:
        return list(self._items.values())


class InMemoryContactRepo:
    def __init__(self) -> None:
        self._items: Dict[int, ContactInfo] = {}
        self._next_id = 1

    def add(self, contact: ContactInfo) -> ContactInfo:
        contact_id = self._next_id
        self._next_id += 1
        created = replace(contact, id=contact_id)
        self._items[contact_id] = created
        return created

    def list_by_user(self, user_id: int) -> List[ContactInfo]:
        return [item for item in self._items.values() if item.user_id == user_id]


class InMemoryLocationRepo:
    def __init__(self) -> None:
        self._items: Dict[int, Location] = {}
        self._next_id = 1

    def add(self, location: Location) -> Location:
        location_id = self._next_id
        self._next_id += 1
        created = replace(location, id=location_id)
        self._items[location_id] = created
        return created

    def get(self, location_id: int) -> Optional[Location]:
        return self._items.get(location_id)

    def list(self) -> List[Location]:
        return list(self._items.values())


class InMemoryCampaignRepo:
    def __init__(self) -> None:
        self._items: Dict[int, Campaign] = {}
        self._next_id = 1

    def add(self, campaign: Campaign) -> Campaign:
        campaign_id = self._next_id
        self._next_id += 1
        created = replace(campaign, id=campaign_id)
        self._items[campaign_id] = created
        return created

    def get(self, campaign_id: int) -> Optional[Campaign]:
        return self._items.get(campaign_id)

    def list(self) -> List[Campaign]:
        return list(self._items.values())


class InMemoryBookingRepo:
    def __init__(self) -> None:
        self._items: Dict[int, Booking] = {}
        self._next_id = 1

    def add(self, booking: Booking) -> Booking:
        booking_id = self._next_id
        self._next_id += 1
        created = replace(booking, id=booking_id)
        self._items[booking_id] = created
        return created

    def list(self) -> List[Booking]:
        return list(self._items.values())

    def list_by_location_date(self, location_id: int, event_date: date) -> List[Booking]:
        return [
            item
            for item in self._items.values()
            if item.location_id == location_id and item.event_date == event_date
        ]
