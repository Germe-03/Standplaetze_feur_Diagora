from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship

Base = declarative_base()


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)

    contact_info: Mapped["ContactInfoModel"] = relationship(
        "ContactInfoModel", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    campaigns: Mapped[list["CampaignModel"]] = relationship("CampaignModel", back_populates="owner")
    bookings: Mapped[list["BookingModel"]] = relationship("BookingModel", back_populates="user")


class ContactInfoModel(Base):
    __tablename__ = "contact_infos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    phone: Mapped[str | None] = mapped_column(String(50))
    address: Mapped[str | None] = mapped_column(String(200))

    user: Mapped[UserModel] = relationship("UserModel", back_populates="contact_info")


class LocationModel(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    city: Mapped[str] = mapped_column(String(120), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    bookings: Mapped[list["BookingModel"]] = relationship("BookingModel", back_populates="location")


class CampaignModel(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    budget: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    owner: Mapped[UserModel] = relationship("UserModel", back_populates="campaigns")
    bookings: Mapped[list["BookingModel"]] = relationship("BookingModel", back_populates="campaign")


class BookingModel(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_date: Mapped[date] = mapped_column(Date, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    location_id: Mapped[int] = mapped_column(Integer, ForeignKey("locations.id"), nullable=False)
    campaign_id: Mapped[int] = mapped_column(Integer, ForeignKey("campaigns.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    location: Mapped[LocationModel] = relationship("LocationModel", back_populates="bookings")
    campaign: Mapped[CampaignModel] = relationship("CampaignModel", back_populates="bookings")
    user: Mapped[UserModel] = relationship("UserModel", back_populates="bookings")
