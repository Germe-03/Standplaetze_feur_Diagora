# Skill: Tests schreiben

Anleitung für Unit-, Integration- und E2E-Tests nach dem Projekt-TDD-Standard.

## Struktur

```
tests/
  unit/
    fakes.py                    # InMemory-Repositories für alle Entitäten
    test_booking_service.py     # Unit Tests für BookingService
    test_campaign_service.py    # Unit Tests für CampaignService
    # weitere test_*_service.py
  integration/
    test_repositories.py        # SQLAlchemy gegen SQLite in-memory
  e2e/
    test_api_flow.py            # FastAPI TestClient, vollständiger Flow
```

## Unit Tests

Testen Services **isoliert** – kein Framework, keine Datenbank, kein HTTP.

```python
# tests/unit/test_mein_service.py
from tests.unit.fakes import InMemoryMeineEntitaetRepo
from BusinessLogic.services import MeineEntitaetService
import pytest

def test_create_erfordert_name():
    svc = MeineEntitaetService(InMemoryMeineEntitaetRepo())
    with pytest.raises(ValueError, match="Name ist erforderlich"):
        svc.create(name="")

def test_create_success():
    svc = MeineEntitaetService(InMemoryMeineEntitaetRepo())
    result = svc.create(name="Test")
    assert result.id is not None
    assert result.name == "Test"
```

## Integration Tests

Testen Repository-Implementierungen gegen echte SQLite-Datenbank (in-memory).

```python
# tests/integration/test_repositories.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from DataAccess.models import Base
from DataAccess.repositories import SqlAlchemyMeineEntitaetRepository
from Model.entities import MeineEntitaet

@pytest.fixture
def session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    s = Session()
    yield s
    s.close()

def test_repository_roundtrip(session):
    repo = SqlAlchemyMeineEntitaetRepository(session)
    created = repo.add(MeineEntitaet(id=None, name="Test"))
    assert created.id is not None
    fetched = repo.get(created.id)
    assert fetched.name == "Test"
```

## E2E Tests

Testen den vollständigen HTTP-Flow über FastAPI TestClient.

```python
# tests/e2e/test_api_flow.py
import pytest
from fastapi.testclient import TestClient
from UI.server import create_app

@pytest.fixture
def client():
    app = create_app("sqlite:///:memory:")
    return TestClient(app)

def test_create_und_list(client):
    r = client.post("/api/meine-entitaeten", json={"name": "Test"})
    assert r.status_code == 201
    assert r.json()["name"] == "Test"

    r = client.get("/api/meine-entitaeten")
    assert r.status_code == 200
    assert len(r.json()) == 1
```

## Fake-Repositories (`tests/unit/fakes.py`)

Jedes Repository-Protocol braucht eine InMemory-Implementierung:

```python
from dataclasses import replace
from typing import List, Optional
from Model.entities import User, ContactInfo, Location, Campaign, Booking

class InMemoryUserRepo:
    def __init__(self): self._store: List[User] = []
    def add(self, u): u = replace(u, id=len(self._store)+1); self._store.append(u); return u
    def get(self, uid): return next((u for u in self._store if u.id == uid), None)
    def list(self): return list(self._store)

# analog für alle weiteren Entitäten
```

## Regeln

- Ein Test testet genau eine Sache
- Test-Namen beschreiben das erwartete Verhalten (`test_create_booking_rejects_past_date`)
- Unit Tests verwenden ausschliesslich Fakes – keine echte DB, kein HTTP
- Integration Tests nutzen SQLite in-memory – kein PostgreSQL nötig
- E2E Tests nutzen `create_app("sqlite:///:memory:")` – kein laufender Server nötig
