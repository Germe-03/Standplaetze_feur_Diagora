from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class User:
    id: Optional[int]
    name: str
    email: str


@dataclass(frozen=True)
class ContactInfo:
    id: Optional[int]
    user_id: int
    phone: Optional[str] = None
    address: Optional[str] = None


@dataclass(frozen=True)
class Location:
    id: Optional[int]
    name: str
    city: str
    price: float


@dataclass(frozen=True)
class Campaign:
    id: Optional[int]
    name: str
    year: int
    budget: float
    owner_id: int


@dataclass(frozen=True)
class Booking:
    id: Optional[int]
    event_date: date
    price: float
    status: str
    location_id: int
    campaign_id: int
    user_id: int
