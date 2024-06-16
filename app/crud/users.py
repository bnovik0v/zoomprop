""" CRUD operations for users. """

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app import models, schemas
from app.utils.auth import get_password_hash


def create_user(db: Session, user: schemas.UserCreate | dict) -> models.User:
    """Create a new user."""
    if isinstance(user, dict):
        data = user
    elif isinstance(user, schemas.UserCreate):
        data = user.model_dump()
    else:
        raise TypeError("user must be a dict or a UserCreate object")

    data["hashed_password"] = get_password_hash(data["password"])
    del data["password"]

    db_user = models.User(**data)
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        existing_user = get_user(db, username=data["username"])
        if existing_user:
            return existing_user
        raise


def get_user(
    db: Session,
    user_id: int | None = None,
    username: str | None = None,
    email: str | None = None,
) -> models.User:
    """Get user."""
    if user_id:
        return db.query(models.User).filter(models.User.id == user_id).first()
    if username:
        return db.query(models.User).filter(models.User.username == username).first()
    if email:
        return db.query(models.User).filter(models.User.email == email).first()
    raise ValueError("user_id, username or email must be provided")


def get_users(
    db: Session,
    limit: int = None,
    sort_by: str | None = None,
    sort_order: str | None = None,
):
    """Get all users or a limited number of users

    Args:
        db (Session): SQLAlchemy session
        limit (int, optional): Number of users to return. Defaults to None.
        sort_by (str, optional): Field to sort by.
        sort_order (str, optional): Sort order.

    Returns:
        List[User]: List of users
    """
    query = db.query(models.User)

    if sort_by and sort_order:
        sort_column = getattr(models.User, sort_by)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())

    if limit:
        query = query.limit(limit)

    return query.all()


def update_user(
    db: Session, user_id: int, user_data: schemas.UserUpdate | dict
) -> models.User:
    """Update a user."""

    if isinstance(user_data, dict):
        data = user_data
    elif isinstance(user_data, schemas.UserUpdate):
        data = user_data.model_dump(exclude_unset=True)
    else:
        raise TypeError("user_data must be a dict or a UserUpdate object")

    if "password" in data:
        data["hashed_password"] = get_password_hash(data["password"])
        del data["password"]

    db.query(models.User).filter(models.User.id == user_id).update(data)
    db.commit()
    return db.query(models.User).filter(models.User.id == user_id).first()


def delete_user(db: Session, user_id: int) -> dict:
    """Delete a user."""
    db.query(models.User).filter(models.User.id == user_id).delete()
    db.commit()
    return {"message": "User deleted"}
