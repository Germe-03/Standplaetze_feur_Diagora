from datetime import date, timedelta

import pytest

from BusinessLogic.services import BookingService, CampaignService, LocationService, UserService
from Model.entities import Booking, Campaign, Location, User
from tests.unit.fakes import (
    InMemoryBookingRepo,
    InMemoryCampaignRepo,
    InMemoryContactRepo,
    InMemoryLocationRepo,
    InMemoryUserRepo,
)


def _seed_user(user_repo: InMemoryUserRepo, contact_repo: InMemoryContactRepo) -> User:
    service = UserService(user_repo, contact_repo)
    return service.create_user(name="Max Muster", email="max@example.com")


def _seed_location(location_repo: InMemoryLocationRepo) -> Location:
    service = LocationService(location_repo)
    return service.create_location(name="Bahnhofplatz", city="Bern", price=120.0)


def _seed_campaign(user: User, campaign_repo: InMemoryCampaignRepo, user_repo: InMemoryUserRepo) -> Campaign:
    service = CampaignService(campaign_repo, user_repo)
    return service.create_campaign(name="Fruehling", year=date.today().year, budget=1000.0, owner_id=user.id)


def test_create_booking_rejects_past_date() -> None:
    user_repo = InMemoryUserRepo()
    contact_repo = InMemoryContactRepo()
    location_repo = InMemoryLocationRepo()
    campaign_repo = InMemoryCampaignRepo()
    booking_repo = InMemoryBookingRepo()

    user = _seed_user(user_repo, contact_repo)
    location = _seed_location(location_repo)
    campaign = _seed_campaign(user, campaign_repo, user_repo)

    service = BookingService(booking_repo, location_repo, campaign_repo, user_repo)

    with pytest.raises(ValueError):
        service.create_booking(
            event_date=date.today() - timedelta(days=1),
            price=100.0,
            status="open",
            location_id=location.id,
            campaign_id=campaign.id,
            user_id=user.id,
        )


def test_create_booking_rejects_double_booking() -> None:
    user_repo = InMemoryUserRepo()
    contact_repo = InMemoryContactRepo()
    location_repo = InMemoryLocationRepo()
    campaign_repo = InMemoryCampaignRepo()
    booking_repo = InMemoryBookingRepo()

    user = _seed_user(user_repo, contact_repo)
    location = _seed_location(location_repo)
    campaign = _seed_campaign(user, campaign_repo, user_repo)
    existing = Booking(
        id=None,
        event_date=date.today() + timedelta(days=7),
        price=150.0,
        status="open",
        location_id=location.id,
        campaign_id=campaign.id,
        user_id=user.id,
    )
    booking_repo.add(existing)

    service = BookingService(booking_repo, location_repo, campaign_repo, user_repo)

    with pytest.raises(ValueError):
        service.create_booking(
            event_date=existing.event_date,
            price=120.0,
            status="confirmed",
            location_id=location.id,
            campaign_id=campaign.id,
            user_id=user.id,
        )


def test_create_booking_success() -> None:
    user_repo = InMemoryUserRepo()
    contact_repo = InMemoryContactRepo()
    location_repo = InMemoryLocationRepo()
    campaign_repo = InMemoryCampaignRepo()
    booking_repo = InMemoryBookingRepo()

    user = _seed_user(user_repo, contact_repo)
    location = _seed_location(location_repo)
    campaign = _seed_campaign(user, campaign_repo, user_repo)

    service = BookingService(booking_repo, location_repo, campaign_repo, user_repo)
    created = service.create_booking(
        event_date=date.today() + timedelta(days=3),
        price=110.0,
        status="open",
        location_id=location.id,
        campaign_id=campaign.id,
        user_id=user.id,
    )

    assert created.id is not None
    assert created.location_id == location.id
