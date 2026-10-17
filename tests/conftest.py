import os

# Tests use an in-memory SQLite DB; skip Liquibase/Postgres startup migrations.
os.environ.setdefault("RUN_MIGRATIONS_ON_STARTUP", "false")

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.adapters.outbound.persistence.orm_models import DepartmentModel
from app.infrastructure.database import Base, get_session
from app.main import app


@pytest.fixture
def session_factory() -> sessionmaker[Session]:
    # A single shared in-memory SQLite connection for the whole test.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(
        bind=engine, autoflush=False, expire_on_commit=False, future=True
    )
    with factory() as seed_session:
        seed_session.add_all(
            [
                DepartmentModel(id=1, department_code="ENG", name="Engineering"),
                DepartmentModel(id=2, department_code="OPS", name="Operations"),
                DepartmentModel(id=3, department_code="HR", name="Human Resources"),
                DepartmentModel(id=4, department_code="FIN", name="Finance"),
            ]
        )
        seed_session.commit()
    return factory


@pytest.fixture
def db_session(session_factory: sessionmaker[Session]) -> Iterator[Session]:
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(session_factory: sessionmaker[Session]) -> Iterator[TestClient]:
    def override_get_session() -> Iterator[Session]:
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
