# tests/crud/test_users.py
from sqlalchemy.orm import Session
from app import crud, schemas


def test_create_user(db: Session):
    user_data = schemas.UserCreate(
        username="testuser", email="testuser@example.com", password="password"
    )
    user = crud.create_user(db, user_data)
    assert user.username == user_data.username


def test_get_user(db: Session):
    user = crud.get_user(db, username="testuser")
    assert user is not None


def test_update_user(db: Session):
    update_data = {"email": "newemail@example.com"}
    user = crud.update_user(db, 1, update_data)
    assert user.email == "newemail@example.com"


def test_delete_user(db: Session):
    response = crud.delete_user(db, 1)
    assert response["message"] == "User deleted"
