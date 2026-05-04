# Skill: Neuen vertikalen Slice hinzufügen

Fügt eine neue Entität vollständig end-to-end hinzu (Model → Port → Service → Repository → API → Tests).

## Schritte

### 1. Entität in `Model/entities.py` ergänzen

```python
@dataclass(frozen=True)
class MeineEntitaet:
    id: Optional[int]
    name: str
    # weitere Felder
```

### 2. Repository-Protocol in `BusinessLogic/ports.py` ergänzen

```python
class MeineEntitaetRepository(Protocol):
    def add(self, obj: MeineEntitaet) -> MeineEntitaet: ...
    def get(self, obj_id: int) -> Optional[MeineEntitaet]: ...
    def list(self) -> List[MeineEntitaet]: ...
```

### 3. Service in `BusinessLogic/services.py` ergänzen

```python
class MeineEntitaetService:
    def __init__(self, repo: MeineEntitaetRepository) -> None:
        self._repo = repo

    def create(self, name: str, ...) -> MeineEntitaet:
        if not name or not name.strip():
            raise ValueError("Name ist erforderlich")
        return self._repo.add(MeineEntitaet(id=None, name=name.strip(), ...))

    def list_all(self) -> List[MeineEntitaet]:
        return self._repo.list()
```

### 4. ORM-Modell in `DataAccess/models.py` ergänzen

```python
class MeineEntitaetModel(Base):
    __tablename__ = "meine_entitaeten"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
```

### 5. Repository-Implementierung in `DataAccess/repositories.py` ergänzen

```python
class SqlAlchemyMeineEntitaetRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, obj: MeineEntitaet) -> MeineEntitaet:
        model = MeineEntitaetModel(name=obj.name)
        self._session.add(model)
        self._session.flush()
        return MeineEntitaet(id=model.id, name=model.name)

    def get(self, obj_id: int) -> Optional[MeineEntitaet]:
        model = self._session.get(MeineEntitaetModel, obj_id)
        return MeineEntitaet(id=model.id, name=model.name) if model else None

    def list(self) -> List[MeineEntitaet]:
        result = self._session.execute(select(MeineEntitaetModel).order_by(MeineEntitaetModel.id))
        return [MeineEntitaet(id=row.id, name=row.name) for row in result.scalars()]
```

### 6. API-Endpunkte in `UI/server.py` ergänzen

```python
class MeineEntitaetCreate(BaseModel):
    name: str

class MeineEntitaetRead(BaseModel):
    id: int
    name: str

# In create_app():
@app.post("/api/meine-entitaeten", response_model=MeineEntitaetRead, status_code=201)
def create_meine_entitaet(payload: MeineEntitaetCreate, services=Depends(get_services)):
    obj = services["meine_entitaeten"].create(name=payload.name)
    return MeineEntitaetRead(id=obj.id, name=obj.name)

@app.get("/api/meine-entitaeten", response_model=list[MeineEntitaetRead])
def list_meine_entitaeten(services=Depends(get_services)):
    return [MeineEntitaetRead(id=o.id, name=o.name) for o in services["meine_entitaeten"].list_all()]
```

### 7. Fake-Repository in `tests/unit/fakes.py` ergänzen

```python
class InMemoryMeineEntitaetRepo:
    def __init__(self): self._store: List[MeineEntitaet] = []
    def add(self, obj): obj = replace(obj, id=len(self._store)+1); self._store.append(obj); return obj
    def get(self, obj_id): return next((o for o in self._store if o.id == obj_id), None)
    def list(self): return list(self._store)
```

### 8. Tests schreiben (siehe `_skills/write-tests.md`)

## Checkliste

- [ ] Entität in `Model/entities.py`
- [ ] Protocol in `BusinessLogic/ports.py`
- [ ] Service in `BusinessLogic/services.py`
- [ ] ORM-Modell in `DataAccess/models.py`
- [ ] Repository in `DataAccess/repositories.py`
- [ ] API-Endpunkte in `UI/server.py`
- [ ] Fake-Repository in `tests/unit/fakes.py`
- [ ] Unit Tests
- [ ] Integration Test
- [ ] E2E Test
