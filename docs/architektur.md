# Architekturdiagramm (1 Seite)

```mermaid
flowchart LR
    UI["UI<br/>(HTTP-Server + Frontend)"]
    BL["BusinessLogic<br/>(Use Cases, Regeln, Workflows)"]
    DA["DataAccess<br/>(Repository, SQL, Persistenzlogik)"]
    DB["SQLite Datenbank<br/>(technisches Speicherdetail)"]
    M["Model<br/>(fachliche Modelle/Regeln)"]

    UI --> BL
    BL --> DA
    DA --> DB
    BL --> M
    DA --> M
```

Abhängigkeitsrichtung gemäß Clean Architecture:

- `Model ← BusinessLogic ← UI`
- `Model ← BusinessLogic ← DataAccess ← Datenbank`

Leserichtung:

- `A ← B` bedeutet: **B hängt von A ab**.
