"""Authentication routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app import crud, schemas
from app.auth import (
    authenticate_user,
    create_tokens_for_user,
    get_user_by_refresh_token,
    verify_access_token,
    oauth2_scheme,
)
from app.utils.auth import get_password_hash
from app.database import get_db
from app.settings import get_settings

settings = get_settings()

router = APIRouter(prefix="/auth")


@router.post("/token", tags=["Authentication"])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """OAuth2 compatible token login, get an access and refresh token for user."""
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return create_tokens_for_user(user)


class TokenRefreshRequest(BaseModel):
    """Token refresh request model."""

    refresh_token: str


@router.post("/token/refresh", tags=["Authentication"])
async def refresh_access_token(
    request_body: TokenRefreshRequest, db: Session = Depends(get_db)
):
    """Refresh access token."""
    user = await get_user_by_refresh_token(request_body.refresh_token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    return create_tokens_for_user(
        {"username": user.username, "is_admin": user.is_admin}
    )


@router.post("/signup", tags=["Authentication"])
async def create_user_signup(
    user_in: schemas.UserCreate,
    db: Session = Depends(get_db),
    auth_token: str = Depends(oauth2_scheme),
):
    """Create new user and return access and refresh tokens."""
    db_user = crud.get_user(db, email=user_in.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user_in.hashed_password = get_password_hash(user_in.password)
    user = crud.create_user(db=db, user=user_in)
    return create_tokens_for_user(
        {"username": user.username, "is_admin": user.is_admin}
    )


@router.post("/verify_token", tags=["Authentication"])
async def verify_token_endpoint(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """Verify JWT token's validity."""
    return await verify_access_token(token, db)
