# Diagora Booking Hub

## Ziel und Use Case

Minimaler, fachlich sinnvoller Use Case: Ein Nutzer legt Standplaetze und Kampagnen an und bucht einen Standplatz fuer ein Datum. Die Buchung ist mit Nutzer, Kampagne und Standplatz verknuepft.

## Architektur

Clean Architecture mit klarer Abhaengigkeitsrichtung:

- Model (Domain): [Model](Model) mit fachlichen Entitaeten
- BusinessLogic (Application): [BusinessLogic](BusinessLogic) mit Use-Case-Services
- UI (Interfaces): [UI](UI) mit FastAPI, REST-Endpunkten und Web-GUI
- DataAccess (Infrastructure): [DataAccess](DataAccess) mit ORM und Repository-Implementierungen

Abhaengigkeiten:

- Model ← BusinessLogic ← UI
- Model ← BusinessLogic ← DataAccess ← Datenbank

Spec/Agent-Dokumentation: siehe [AGENTS.md](AGENTS.md)

## Entitaeten und Use Cases

Entitaeten (mindestens 5): User, ContactInfo, Location (Standplatz), Campaign, Booking

Use Cases als Services (mindestens 2):

- UserService, LocationService, CampaignService, BookingService

## REST API und OpenAPI

- REST-Endpunkte unter `/api/*`
- OpenAPI/Swagger automatisch unter `/docs` und `/openapi.json`

## Setup

### Voraussetzungen

- Python 3.12+
- Optional: PostgreSQL fuer Produktion/Cloud

### Lokales Starten

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python UI\server.py
```

Default ist SQLite unter `Databank/app.db`. Fuer PostgreSQL:

```powershell
$env:DATABASE_URL="postgresql+psycopg://app:app@localhost:5432/diagora"
python UI\server.py
```

UI: http://127.0.0.1:8080/

## Tests (TDD)

```powershell
pip install -r requirements-dev.txt
pytest
```

Testarten:

- Unit: [tests/unit](tests/unit)
- Integration: [tests/integration](tests/integration)
- E2E: [tests/e2e](tests/e2e)

## Docker

```bash
docker build -t diagora-booking-hub .
docker run -p 8080:8080 -e DATABASE_URL=postgresql+psycopg://app:app@host.docker.internal:5432/diagora diagora-booking-hub
```

Optional lokal mit PostgreSQL:

```bash
docker compose up --build
```

## CI, Release, CD

- CI: Tests bei Push/PR
- Release: Tag `v*` erstellt GitHub Release und Docker-Image
- CD: Workflow triggert Render Deploy Hook (Secret erforderlich)

Details: [.github/workflows](.github/workflows)

## Cloud Deployment (Beispiel Render)

- Render Web Service mit `Dockerfile`
- PostgreSQL als Render Database
- `DATABASE_URL` in Render setzen
- Deploy Hook URL als GitHub Secret `RENDER_DEPLOY_HOOK_URL`
- Optionale Blueprint-Definition: [render.yaml](render.yaml)

## Projektanforderungen (Erfuellung)

- Enterprise-grade Architektur: Clean Architecture mit getrennten Schichten
- TDD: Unit-, Integration-, E2E-Tests
- ORM + relationale DB: SQLAlchemy + PostgreSQL
- REST API + OpenAPI
- Web-GUI: UI/index.html + UI/app.js
- CI, Release, CD, Docker, Cloud-Deployment
