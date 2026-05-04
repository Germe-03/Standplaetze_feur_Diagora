# AGENTS.md – Diagora Booking Hub

## Projektüberblick

Buchungssystem für Standplätze (Locations) im Kontext von Marketingkampagnen.
Ein Nutzer legt Standplätze und Kampagnen an und bucht einen Standplatz für ein Datum.

## Coding-Agent-Einsatz

Dieses Projekt wurde mit **Claude Code (Anthropic)** als primärem Coding-Agent entwickelt.

### Wie der Agent eingesetzt wurde

- **Architektur-Refactoring**: Die ursprüngliche Implementierung nutzte direkte SQLite-Abfragen und tightly-coupled Manager-Klassen. Claude Code wurde eingesetzt, um die gesamte Codebasis auf Clean Architecture umzubauen – mit klarer Schichtentrennung, Dependency Inversion und SQLAlchemy ORM.
- **Spec-Driven Development**: Diese AGENTS.md-Datei dient als Spec. Vor jeder Implementierung wurde die gewünschte Architektur hier definiert; Claude Code hält sich strikt daran.
- **TDD-Unterstützung**: Tests wurden gemeinsam mit der Implementierung erarbeitet. Claude Code schreibt Tests vor oder parallel zur Implementierung.
- **Vertikale Slices**: Neue Features werden als vollständige Slices (Entity → Service → Repository → API-Endpoint → Tests) implementiert.

### Werkzeuge

| Tool | Zweck |
|---|---|
| Claude Code (CLI) | Primärer Coding-Agent (Architektur, Tests, Refactoring) |
| GitHub Copilot | Inline-Vervollständigung im Editor |
| FastAPI | REST API Framework |
| SQLAlchemy 2.0 | ORM |
| pytest | Test-Framework |
| GitHub Actions | CI/CD |
| Docker | Containerisierung |
| Render | Cloud-Deployment |

## Architektur (Clean Architecture)

```
Model (Domain)
  ↑
BusinessLogic (Application) ← ports.py (Protokolle/Interfaces)
  ↑                                    ↑
UI (Interfaces/FastAPI)        DataAccess (Infrastructure/SQLAlchemy)
```

### Schichten

| Schicht | Ordner | Inhalt |
|---|---|---|
| Domain | `Model/` | Frozen Dataclasses, keine externen Abhängigkeiten |
| Application | `BusinessLogic/` | Services, Use Cases, Ports (Protocols) |
| Interfaces | `UI/` | FastAPI, Pydantic-Schemas, REST-Endpunkte |
| Infrastructure | `DataAccess/` | SQLAlchemy-Modelle, Repository-Implementierungen, DB-Setup |

### Abhängigkeitsregel

- Innere Schichten kennen äussere **nicht**
- `Model` importiert nichts aus dem Projekt
- `BusinessLogic` importiert nur `Model` und eigene `ports.py`
- `DataAccess` importiert `Model` und SQLAlchemy
- `UI` verdrahtet alles via Dependency Injection

## Regeln für den Coding-Agent

- Nutze Deutsch für alle generierten Texte und Fehlermeldungen.
- Bevorzuge es, bestehende Artefakte zu aktualisieren, statt neue zu erstellen.
- Halte Artefakte so schlank wie möglich; keine unnötigen Kommentare.
- Folge TDD: Tests vor oder parallel zur Implementierung.
- Neue Entitäten immer als vertikaler Slice (Model → Port → Service → Repository → API-Endpoint → Tests).
- Neue Repositories müssen das entsprechende Protocol in `ports.py` implementieren.
- Neue Services erhalten Fake-Repositories für Unit Tests (in `tests/unit/fakes.py`).
- Keine Business-Logik in `UI/server.py` – nur HTTP-Mapping.
- Keine Datenbankdetails in `BusinessLogic/` – nur Ports verwenden.
- Bei unklaren Anforderungen oder Architekturentscheidungen: Nutzer fragen.

## Test-Strategie

```
tests/
  unit/          # Services mit InMemory-Fake-Repositories (kein DB, kein HTTP)
  integration/   # SQLAlchemy-Repositories gegen SQLite in-memory
  e2e/           # FastAPI TestClient gegen komplette App
  unit/fakes.py  # InMemory-Implementierungen aller Repository-Protokolle
```

- Unit Tests testen Business-Logik isoliert (kein Framework-Code)
- Integration Tests validieren ORM-Mapping und SQL-Korrektheit
- E2E Tests validieren den vollständigen HTTP-Flow

## Lokale Entwicklung

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt
python UI/server.py
# API: http://127.0.0.1:8080/
# Swagger: http://127.0.0.1:8080/docs
```

Tests ausführen:
```bash
pytest
```

## Skills

Projektspezifische Anleitungen für wiederkehrende Aufgaben:

- Neuen vertikalen Slice hinzufügen: [`_skills/new-slice.md`](_skills/new-slice.md)
- Tests schreiben: [`_skills/write-tests.md`](_skills/write-tests.md)
