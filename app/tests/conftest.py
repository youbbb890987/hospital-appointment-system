import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture
def admin_token(client):
    client.post("/auth/register", json={
        "name": "Admin",
        "email": "admin@test.com",
        "password": "admin123",
        "role": "admin"
    })
    res = client.post("/auth/login", data={
        "username": "admin@test.com",
        "password": "admin123"
    })
    return res.json()["access_token"]


@pytest.fixture
def user_token(client):
    client.post("/auth/register", json={
        "name": "User",
        "email": "user@test.com",
        "password": "user123",
        "role": "patient"
    })
    res = client.post("/auth/login", data={
        "username": "user@test.com",
        "password": "user123"
    })
    return res.json()["access_token"]


@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def user_headers(user_token):
    return {"Authorization": f"Bearer {user_token}"}