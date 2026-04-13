# Diagora Booking Hub

## Ziel des Projekts

Diese Anwendung verwaltet Standplätze und deren Buchungen inkl. Kampagnen, Nutzerverwaltung, Kalenderansicht und Dashboard-Auswertung.

Die UI läuft als einfache Webanwendung über einen Python-HTTP-Server und greift auf eine SQLite-Datenbank zu.

## Starten

Im Projektordner:

```powershell
py -3.12 UI\server.py --host 127.0.0.1 --port 8091
```

Dann im Browser öffnen:

`http://127.0.0.1:8091/`

## API-Dokumentation (OpenAPI)

- OpenAPI-Datei: [`docs/openapi.yaml`](docs/openapi.yaml)

## Testpyramide

Diese Codebasis nutzt eine sichtbare Testpyramide mit drei Ebenen:

- **Unit**: schnelle, isolierte Tests von Modellen/Funktionen
- **Integration**: Zusammenspiel von BusinessLogic und DataAccess
- **E2E**: API-Endpunkte über den HTTP-Server

Beispiel-Commands:

```bash
python -m unittest discover -s tests/unit -p "test_*.py" -v
python -m unittest discover -s tests/integration -p "test_*.py" -v
python -m unittest discover -s tests/e2e -p "test_*.py" -v
```

Alle Ebenen zusammen:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

## CI (PR-Gates)

- Workflow-Datei: [`.github/workflows/ci.yml`](.github/workflows/ci.yml)
- Der Workflow führt Unit-, Integration- und E2E-Tests aus.
- Damit PRs **nur mit grünen Tests** mergebar sind, muss in GitHub der Status-Check `CI / test-pyramid` als Required Check in den Branch Protection Rules aktiviert sein.

## Docker

Dockerfile ist vorhanden: [`Dockerfile`](Dockerfile)

Build:

```bash
docker build -t diagora-booking-hub .
```

Start:

```bash
docker run --rm -p 10000:10000 diagora-booking-hub
```

Dann im Browser öffnen:

`http://127.0.0.1:10000/`

## Render-Deploy

- Anleitung: [`docs/render-deploy.md`](docs/render-deploy.md)

## Architekturdiagramm

- Diagramm (1 Seite): [`docs/architektur.md`](docs/architektur.md)

## Reiter im Frontend

### 1) Dashboard

Zweck:
- Schneller Überblick über Buchungsstatus und Kosten.

Funktionen:
- Jahres- und Monatskennzahlen:
  - Buchungen (ohne storniert)
  - Offene Buchungen
  - Bestätigte Buchungen
  - Kosten/Umsatz
- Kampagnenfilter für Jahres- und Monatsauswertung.
- Diagramme für:
  - Anzahl bestätigte Buchungen
  - Kosten bestätigte Buchungen
  - Budget-Status

### 2) Kalender

Zweck:
- Zeitliche Sicht auf Buchungen und belegte Standplätze.

Funktionen:
- Ansichten: Monat, Woche, Arbeitswoche.
- Navigation: Zurück, Heute, Weiter.
- Direkter Sprung von Kalendereinträgen zu Buchungen (Bearbeitungsmodus).

### 3) Buchungen

Zweck:
- Buchungen erfassen, validieren und bearbeiten.

Funktionen:
- Neue Buchung und Bearbeiten bestehender Buchungen.
- Live-Validierung von Limits (jährlich/monatlich/kampagnenbezogen).
- Anzeige von Fehlermeldungen direkt im Formular.
- Speichern wird bei ungültigen Daten blockiert.
- Tabellenansicht mit Sortierung und Spaltenfilter.
- Scroll-Container für große Tabellen (ab >10 Einträgen).

### 4) Standplätze

Zweck:
- Standplätze und Limits zentral verwalten.

Funktionen:
- Erfassung/Bearbeitung von Stammdaten:
  - Name, Stadt, Kanton, Preis, Rating, Max Dialog, Notiz, SBB-Flag
- Verwaltung von Limits:
  - Jahr, Monat, Kampagne, gültig ab
- Tabelle mit Restkontingenten und Limit-Informationen.
- Sortierung/Filter analog Buchungen.

### 5) Kampagnen verwalten

Zweck:
- Kampagnen anlegen, suchen, filtern und bearbeiten.

Funktionen:
- Formular für neue Kampagne oder Bearbeiten einer ausgewählten Kampagne.
- Suche nach Name/Benutzer.
- Filter:
  - Jahr
  - Benutzer
  - Aktivstatus (Standard: nur aktive)
- Aktivstatus pro Kampagne (`IsActive`).
- Löschfunktion nur erlaubt, wenn keine Buchung mit der Kampagne verknüpft ist.

### 6) Nutzer verwalten

Zweck:
- Benutzerstammdaten und Rollen administrieren.

Funktionen:
- Formular für neuen Nutzer oder Bearbeitung.
- Rollen sind fest begrenzt auf:
  - `Admin`
  - `User`
  - `Viewer` (Anzeige in UI: `Betrachter`)
- Pflichtfeld beim Erstellen:
  - E-Mail
- Optionale Kontaktdaten:
  - Telefon
  - Adresse als einzelne Felder:
    - Straße
    - Nummer
    - PLZ
    - Ort
    - Kanton
- Filter:
  - Suche
  - Rolle
  - Aktivstatus (Standard: nur aktive)
- Löschfunktion nur erlaubt, wenn keine Buchungen und keine Standplätze mit dem Nutzer verknüpft sind.
- Nutzer-ID-Wiederverwendung:
  - Bei Löschung wird die kleinste freie UserID beim nächsten Erstellen erneut genutzt.

## Projektstruktur

### `Model/`

Enthält die Datenobjekte (Domänenmodelle), z. B.:
- `User`
- `Campaign`
- `Booking`
- `Location`
- `Address`
- `ContactInformation`

Aufgabe:
- Kapselung von Entitäten und Feldvalidierung auf Objektebene.

### `DataAccess/`

Enthält den Zugriff auf SQLite (SQL-Queries), z. B.:
- `UserDataAccess`
- `CampaignDataAccess`
- `BookingDataAccess`
- `LocationsDataAccess`
- `AddressDataAccess`
- `ContactInformationDataAccess`

Aufgabe:
- Lesen/Schreiben/Löschen der Datenbankeinträge.
- Technische Migrationen bei Bedarf (z. B. `IsActive`-Felder).

### `BusinessLogic/`

Enthält die Fachlogik (Regeln, Validierungen, Workflows), z. B.:
- `BookingManager`
- `LocationsManager`
- `CampaignManager`
- `UserManager`
- `WebAppManager` als zentrale Schicht für UI/API.

Aufgabe:
- Durchsetzen fachlicher Regeln (z. B. Limits, erlaubte Rollen, Löschbedingungen).
- Zusammenführen mehrerer DataAccess-Operationen zu einem Use Case.

### `UI/`

Frontend + kleiner API-Server:
- `server.py`: HTTP-Endpunkte (`/api/...`) und Auslieferung statischer Dateien.
- `index.html`, `styles.css`: Layout/Styling.
- JS-Dateien je Bereich:
  - `dashboard.js`
  - `calendar.js`
  - `bookings.js`
  - `stands.js`
  - `campaigns.js`
  - `users.js`
- Gemeinsamer Code:
  - `CommonCodeApp.js`
  - `CommonCodeDashboardCalender.js`
  - `CommonCodeBookingsStandplaetze.js`

Aufgabe:
- Bedienlogik pro Reiter
- API-Aufrufe
- Rendering der Tabellen/Formulare/Diagramme

## Request-Fluss (vereinfacht)

1. Nutzeraktion im Browser (z. B. Speichern einer Buchung).
2. `UI/*.js` sendet Request an `UI/server.py`.
3. `server.py` ruft Methode im `WebAppManager` auf.
4. `WebAppManager` nutzt passende Manager in `BusinessLogic`.
5. Manager greifen über `DataAccess` auf SQLite zu.
6. Antwort wird als JSON an die UI zurückgegeben und dargestellt.

## Wichtige Regeln im System

- Buchungen werden gegen Standort-/Stadtlimits geprüft.
- Rollen sind strikt auf `Admin/User/Viewer` begrenzt.
- E-Mail ist beim Erstellen eines Nutzers Pflicht.
- Kontakt- und Adressinfos können optional ergänzt werden.
- Löschen ist bei verknüpften Daten restriktiv abgesichert.

## Datenbankhinweise

Aktuell relevante Erweiterungen:
- `Users.IsActive` (Default aktiv)
- `Campaign.IsActive` (Default aktiv)

Migrationen für diese Felder werden zur Laufzeit automatisch geprüft und bei Bedarf ausgeführt.
