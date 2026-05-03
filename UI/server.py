from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
UI_ROOT = PROJECT_ROOT / "UI"

from fastapi import Depends, FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from BusinessLogic.services import BookingService, CampaignService, LocationService, UserService
from DataAccess.db import build_engine, build_session_factory, init_db
from DataAccess.repositories import (
    SqlAlchemyBookingRepository,
    SqlAlchemyCampaignRepository,
    SqlAlchemyContactRepository,
    SqlAlchemyLocationRepository,
    SqlAlchemyUserRepository,
)


class UserCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None


class UserRead(BaseModel):
    id: int
    name: str
    email: str


class LocationCreate(BaseModel):
    name: str
    city: str
    price: float


class LocationRead(BaseModel):
    id: int
    name: str
    city: str
    price: float


class CampaignCreate(BaseModel):
    name: str
    year: int
    budget: float
    owner_id: int


class CampaignRead(BaseModel):
    id: int
    name: str
    year: int
    budget: float
    owner_id: int


class BookingCreate(BaseModel):
    event_date: date
    price: float
    status: str
    location_id: int
    campaign_id: int
    user_id: int


class BookingRead(BaseModel):
    id: int
    event_date: date
    price: float
    status: str
    location_id: int
    campaign_id: int
    user_id: int


def create_app(database_url: Optional[str] = None) -> FastAPI:
    engine = build_engine(database_url)
    init_db(engine)
    SessionLocal = build_session_factory(engine)

    app = FastAPI(title="Diagora Booking Hub", version="1.0.0")

    @app.exception_handler(ValueError)
    async def value_error_handler(_, exc: ValueError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    def get_session():
        session = SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_services(session: Session = Depends(get_session)):
        user_repo = SqlAlchemyUserRepository(session)
        contact_repo = SqlAlchemyContactRepository(session)
        location_repo = SqlAlchemyLocationRepository(session)
        campaign_repo = SqlAlchemyCampaignRepository(session)
        booking_repo = SqlAlchemyBookingRepository(session)

        return {
            "users": UserService(user_repo, contact_repo),
            "locations": LocationService(location_repo),
            "campaigns": CampaignService(campaign_repo, user_repo),
            "bookings": BookingService(booking_repo, location_repo, campaign_repo, user_repo),
        }

    @app.get("/api/health")
    def health_check():
        return {"status": "ok"}

    @app.post("/api/users", response_model=UserRead, status_code=201)
    def create_user(payload: UserCreate, services=Depends(get_services)):
        user = services["users"].create_user(
            name=payload.name,
            email=payload.email,
            phone=payload.phone,
            address=payload.address,
        )
        return UserRead(id=user.id, name=user.name, email=user.email)

    @app.get("/api/users", response_model=list[UserRead])
    def list_users(services=Depends(get_services)):
        return [UserRead(id=item.id, name=item.name, email=item.email) for item in services["users"].list_users()]

    @app.post("/api/locations", response_model=LocationRead, status_code=201)
    def create_location(payload: LocationCreate, services=Depends(get_services)):
        location = services["locations"].create_location(
            name=payload.name,
            city=payload.city,
            price=payload.price,
        )
        return LocationRead(id=location.id, name=location.name, city=location.city, price=location.price)

    @app.get("/api/locations", response_model=list[LocationRead])
    def list_locations(services=Depends(get_services)):
        return [
            LocationRead(id=item.id, name=item.name, city=item.city, price=item.price)
            for item in services["locations"].list_locations()
        ]

    @app.post("/api/campaigns", response_model=CampaignRead, status_code=201)
    def create_campaign(payload: CampaignCreate, services=Depends(get_services)):
        campaign = services["campaigns"].create_campaign(
            name=payload.name,
            year=payload.year,
            budget=payload.budget,
            owner_id=payload.owner_id,
        )
        return CampaignRead(
            id=campaign.id,
            name=campaign.name,
            year=campaign.year,
            budget=campaign.budget,
            owner_id=campaign.owner_id,
        )

    @app.get("/api/campaigns", response_model=list[CampaignRead])
    def list_campaigns(services=Depends(get_services)):
        return [
            CampaignRead(
                id=item.id,
                name=item.name,
                year=item.year,
                budget=item.budget,
                owner_id=item.owner_id,
            )
            for item in services["campaigns"].list_campaigns()
        ]

    @app.post("/api/bookings", response_model=BookingRead, status_code=201)
    def create_booking(payload: BookingCreate, services=Depends(get_services)):
        booking = services["bookings"].create_booking(
            event_date=payload.event_date,
            price=payload.price,
            status=payload.status,
            location_id=payload.location_id,
            campaign_id=payload.campaign_id,
            user_id=payload.user_id,
        )
        return BookingRead(
            id=booking.id,
            event_date=booking.event_date,
            price=booking.price,
            status=booking.status,
            location_id=booking.location_id,
            campaign_id=booking.campaign_id,
            user_id=booking.user_id,
        )

    @app.get("/api/bookings", response_model=list[BookingRead])
    def list_bookings(services=Depends(get_services)):
        return [
            BookingRead(
                id=item.id,
                event_date=item.event_date,
                price=item.price,
                status=item.status,
                location_id=item.location_id,
                campaign_id=item.campaign_id,
                user_id=item.user_id,
            )
            for item in services["bookings"].list_bookings()
        ]

    @app.get("/")
    def root():
        return FileResponse(UI_ROOT / "index.html")

    app.mount("/static", StaticFiles(directory=UI_ROOT), name="static")

    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(create_app(), host="0.0.0.0", port=8080)
