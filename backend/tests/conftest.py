import os
from collections.abc import Generator

# These non-secret values are only for importing the app during tests.
os.environ.setdefault("DB_PASSWORD", "test-database-password")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret-key-that-is-not-used-outside-tests")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.db.base import Base
from app.main import app
from app.models import Project, Task, User  # noqa: F401 - registers all metadata

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def isolated_database(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db] = override_get_db
    # /health imports this name directly, so replace it for the test app too.
    monkeypatch.setattr("app.main.SessionLocal", TestingSessionLocal)
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


def register_and_login(client: TestClient, email: str) -> dict[str, str]:
    password = "a-safe-test-password"
    register = client.post("/api/v1/auth/register", json={"email": email, "password": password})
    assert register.status_code == 201, register.text
    login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200, login.text
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


@pytest.fixture
def user_headers(client: TestClient) -> dict[str, str]:
    return register_and_login(client, "owner@example.com")


@pytest.fixture
def second_user_headers(client: TestClient) -> dict[str, str]:
    return register_and_login(client, "other@example.com")


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
