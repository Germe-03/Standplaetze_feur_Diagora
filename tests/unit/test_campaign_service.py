from datetime import date

import pytest

from BusinessLogic.services import CampaignService, UserService
from tests.unit.fakes import InMemoryCampaignRepo, InMemoryContactRepo, InMemoryUserRepo


def test_create_campaign_requires_owner() -> None:
    user_repo = InMemoryUserRepo()
    contact_repo = InMemoryContactRepo()
    campaign_repo = InMemoryCampaignRepo()

    service = CampaignService(campaign_repo, user_repo)

    with pytest.raises(ValueError):
        service.create_campaign(name="Sommer", year=date.today().year, budget=500.0, owner_id=999)


def test_create_campaign_success() -> None:
    user_repo = InMemoryUserRepo()
    contact_repo = InMemoryContactRepo()
    campaign_repo = InMemoryCampaignRepo()

    user_service = UserService(user_repo, contact_repo)
    user = user_service.create_user(name="Nina Beispiel", email="nina@example.com")

    service = CampaignService(campaign_repo, user_repo)
    created = service.create_campaign(name="Sommer", year=date.today().year, budget=500.0, owner_id=user.id)

    assert created.id is not None
    assert created.owner_id == user.id
