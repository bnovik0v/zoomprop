"""Test fixtures for the FastAPI app."""

import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.database import Base, get_db
from app.main import app
from app.settings import get_settings
from app.models import User, Property

settings = get_settings()
DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def db():
    """Create a clean database for testing."""
    Base.metadata.create_all(bind=engine)
    print("Tables created")
    inspector = inspect(engine)
    print("Tables in the database:", inspector.get_table_names())
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after the test
        Base.metadata.drop_all(bind=engine)
        print("Tables dropped")
        print("Tables in the database after drop:", inspector.get_table_names())


@pytest.fixture(scope="module")
def client(db):
    """Get a FastAPI test client."""

    def _get_test_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides[get_db] = get_db


@pytest.fixture(scope="module")
def auth_headers(client: TestClient):
    """Get authorization headers."""
    headers = {"Authorization": f"Bearer token"}
    return headers


def test_setup(db):
    """Test database setup."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "users" in tables, "users table was not created"
    assert "properties" in tables, "properties table was not created"
