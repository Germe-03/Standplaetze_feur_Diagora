from __future__ import annotations

import os
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from DataAccess.models import Base


def build_engine(database_url: Optional[str] = None) -> Engine:
    url = database_url or os.getenv("DATABASE_URL") or "sqlite+pysqlite:///./Databank/app.db"
    if url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
        if url.endswith(":memory:"):
            return create_engine(url, connect_args=connect_args, poolclass=StaticPool)
        return create_engine(url, connect_args=connect_args)
    return create_engine(url)


def build_session_factory(engine: Engine):
    return sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)


def init_db(engine: Engine) -> None:
    Base.metadata.create_all(bind=engine)
