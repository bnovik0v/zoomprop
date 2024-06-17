""" Users route """

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import crud, schemas, models
from app.database import get_db
from app.auth import oauth2_scheme
from app.auth import get_current_user, requre_admin_user

router = APIRouter(
    prefix="/api",
    tags=["Users"],
)


@router.post("/users/", response_model=schemas.User)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    auth_token: str = Depends(oauth2_scheme),
    _admin: models.User = Depends(requre_admin_user),
):
    """Create a new user."""
    db_user = crud.get_user(db=db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@router.get("/users/me", response_model=schemas.User)
def read_user_me(
    current_user: str = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get current user."""
    db_user = crud.get_user(db=db, username=current_user["username"])
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.get("/users/{user_id}", response_model=schemas.User)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    auth_token: str = Depends(oauth2_scheme),
):
    """Get a user."""
    db_user = crud.get_user(db=db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.get("/users/", response_model=List[schemas.User])
def read_users(
    limit: int | None = None,
    sort_by: str | None = Query(None, pattern="^(creation_date|update_date|id)$"),
    sort_order: str | None = Query(None, pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    auth_token: str = Depends(oauth2_scheme),
):
    """Get all users or a limited number of users."""
    return crud.get_users(db=db, limit=limit, sort_by=sort_by, sort_order=sort_order)


@router.put("/users/{user_id}", response_model=schemas.User)
def update_user(
    user_id: int,
    user: schemas.UserUpdate,
    db: Session = Depends(get_db),
    auth_token: str = Depends(oauth2_scheme),
    _admin: models.User = Depends(requre_admin_user),
):
    """Update a user."""
    db_user = crud.get_user(db=db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.update_user(db=db, user_id=user_id, user_data=user)


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    auth_token: str = Depends(oauth2_scheme),
    _admin: models.User = Depends(requre_admin_user),
):
    """Delete a user."""
    db_user = crud.get_user(db=db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.delete_user(db=db, user_id=user_id)
