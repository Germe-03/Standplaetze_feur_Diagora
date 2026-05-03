from datetime import date, timedelta

from DataAccess.db import build_engine, build_session_factory, init_db
from DataAccess.repositories import (
    SqlAlchemyBookingRepository,
    SqlAlchemyCampaignRepository,
    SqlAlchemyContactRepository,
    SqlAlchemyLocationRepository,
    SqlAlchemyUserRepository,
)
from Model.entities import Booking, Campaign, ContactInfo, Location, User


def test_repository_roundtrip() -> None:
    engine = build_engine("sqlite+pysqlite:///:memory:")
    init_db(engine)
    SessionLocal = build_session_factory(engine)

    session = SessionLocal()
    try:
        user_repo = SqlAlchemyUserRepository(session)
        contact_repo = SqlAlchemyContactRepository(session)
        location_repo = SqlAlchemyLocationRepository(session)
        campaign_repo = SqlAlchemyCampaignRepository(session)
        booking_repo = SqlAlchemyBookingRepository(session)

        user = user_repo.add(User(id=None, name="Mara Beispiel", email="mara@example.com"))
        contact_repo.add(ContactInfo(id=None, user_id=user.id, phone="+41 79 000 00 00", address="Bahnhofstrasse 1"))
        location = location_repo.add(Location(id=None, name="Altstadt", city="Bern", price=120.0))
        campaign = campaign_repo.add(
            Campaign(id=None, name="Herbst", year=date.today().year, budget=1500.0, owner_id=user.id)
        )
        booking = booking_repo.add(
            Booking(
                id=None,
                event_date=date.today() + timedelta(days=10),
                price=120.0,
                status="open",
                location_id=location.id,
                campaign_id=campaign.id,
                user_id=user.id,
            )
        )
        session.commit()

        bookings = booking_repo.list()
        assert len(bookings) == 1
        assert bookings[0].id == booking.id
    finally:
        session.close()
