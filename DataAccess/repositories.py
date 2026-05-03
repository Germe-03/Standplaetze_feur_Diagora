from __future__ import annotations

from datetime import date
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from Model.entities import Booking, Campaign, ContactInfo, Location, User
from DataAccess.models import BookingModel, CampaignModel, ContactInfoModel, LocationModel, UserModel


class SqlAlchemyUserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, user: User) -> User:
        model = UserModel(name=user.name, email=user.email)
        self._session.add(model)
        self._session.flush()
        return User(id=model.id, name=model.name, email=model.email)

    def get(self, user_id: int) -> Optional[User]:
        model = self._session.get(UserModel, user_id)
        if not model:
            return None
        return User(id=model.id, name=model.name, email=model.email)

    def list(self) -> List[User]:
        result = self._session.execute(select(UserModel).order_by(UserModel.id))
        return [User(id=row.id, name=row.name, email=row.email) for row in result.scalars()]


class SqlAlchemyContactRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, contact: ContactInfo) -> ContactInfo:
        model = ContactInfoModel(user_id=contact.user_id, phone=contact.phone, address=contact.address)
        self._session.add(model)
        self._session.flush()
        return ContactInfo(id=model.id, user_id=model.user_id, phone=model.phone, address=model.address)

    def list_by_user(self, user_id: int) -> List[ContactInfo]:
        result = self._session.execute(
            select(ContactInfoModel).where(ContactInfoModel.user_id == user_id)
        )
        return [
            ContactInfo(id=row.id, user_id=row.user_id, phone=row.phone, address=row.address)
            for row in result.scalars()
        ]


class SqlAlchemyLocationRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, location: Location) -> Location:
        model = LocationModel(name=location.name, city=location.city, price=location.price)
        self._session.add(model)
        self._session.flush()
        return Location(id=model.id, name=model.name, city=model.city, price=float(model.price))

    def get(self, location_id: int) -> Optional[Location]:
        model = self._session.get(LocationModel, location_id)
        if not model:
            return None
        return Location(id=model.id, name=model.name, city=model.city, price=float(model.price))

    def list(self) -> List[Location]:
        result = self._session.execute(select(LocationModel).order_by(LocationModel.id))
        return [
            Location(id=row.id, name=row.name, city=row.city, price=float(row.price))
            for row in result.scalars()
        ]


class SqlAlchemyCampaignRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, campaign: Campaign) -> Campaign:
        model = CampaignModel(
            name=campaign.name,
            year=campaign.year,
            budget=campaign.budget,
            owner_id=campaign.owner_id,
        )
        self._session.add(model)
        self._session.flush()
        return Campaign(
            id=model.id,
            name=model.name,
            year=model.year,
            budget=float(model.budget),
            owner_id=model.owner_id,
        )

    def get(self, campaign_id: int) -> Optional[Campaign]:
        model = self._session.get(CampaignModel, campaign_id)
        if not model:
            return None
        return Campaign(
            id=model.id,
            name=model.name,
            year=model.year,
            budget=float(model.budget),
            owner_id=model.owner_id,
        )

    def list(self) -> List[Campaign]:
        result = self._session.execute(select(CampaignModel).order_by(CampaignModel.id))
        return [
            Campaign(
                id=row.id,
                name=row.name,
                year=row.year,
                budget=float(row.budget),
                owner_id=row.owner_id,
            )
            for row in result.scalars()
        ]


class SqlAlchemyBookingRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, booking: Booking) -> Booking:
        model = BookingModel(
            event_date=booking.event_date,
            price=booking.price,
            status=booking.status,
            location_id=booking.location_id,
            campaign_id=booking.campaign_id,
            user_id=booking.user_id,
        )
        self._session.add(model)
        self._session.flush()
        return Booking(
            id=model.id,
            event_date=model.event_date,
            price=float(model.price),
            status=model.status,
            location_id=model.location_id,
            campaign_id=model.campaign_id,
            user_id=model.user_id,
        )

    def list(self) -> List[Booking]:
        result = self._session.execute(select(BookingModel).order_by(BookingModel.id))
        return [
            Booking(
                id=row.id,
                event_date=row.event_date,
                price=float(row.price),
                status=row.status,
                location_id=row.location_id,
                campaign_id=row.campaign_id,
                user_id=row.user_id,
            )
            for row in result.scalars()
        ]

    def list_by_location_date(self, location_id: int, event_date: date) -> List[Booking]:
        result = self._session.execute(
            select(BookingModel).where(
                BookingModel.location_id == location_id, BookingModel.event_date == event_date
            )
        )
        return [
            Booking(
                id=row.id,
                event_date=row.event_date,
                price=float(row.price),
                status=row.status,
                location_id=row.location_id,
                campaign_id=row.campaign_id,
                user_id=row.user_id,
            )
            for row in result.scalars()
        ]
