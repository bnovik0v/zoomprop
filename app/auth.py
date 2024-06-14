""" Authentication module for a FastAPI application. """

import logging
from datetime import datetime, timedelta
from typing import Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app import crud
from app.utils.auth import verify_password
from app.database import get_db
from app.settings import get_settings

logger = logging.getLogger(__name__)
logging.getLogger("passlib").setLevel(logging.ERROR)

settings = get_settings()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def create_token(data: dict, expires_delta: timedelta, secret_key: str) -> str:
    """Generalized function to create JWT tokens."""
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "iss": "your_issuer"})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def create_access_token(data: dict, expires_minutes: Optional[int] = None) -> str:
    """Create an access token."""
    expires_delta = timedelta(
        minutes=expires_minutes if expires_minutes else ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return create_token(data, expires_delta, settings.secret_key)


def create_refresh_token(data: dict, expires_minutes: Optional[int] = None) -> str:
    """Create a refresh token."""
    expires_delta = timedelta(
        minutes=expires_minutes if expires_minutes else REFRESH_TOKEN_EXPIRE_MINUTES
    )
    return create_token(data, expires_delta, settings.refresh_secret_key)


def authenticate_user(username: str, password: str, db: Session) -> Union[dict, bool]:
    """Authenticate a user by username and password."""
    user = crud.get_user(db, username=username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return {"username": user.username, "is_admin": user.is_admin}


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """Retrieve the current user from the token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            logger.error("Username not found in token")
            raise credentials_exception
        user = crud.get_user(db, username=username)
        if not user:
            logger.error("User not found in database")
            raise credentials_exception
        token_data = {"username": user.username, "is_admin": user.is_admin}
    except JWTError as e:
        logger.error("JWT Error: %s", e)
        raise credentials_exception from None
    return token_data


def requre_admin_user(current_user: dict = Depends(get_current_user)):
    """Ensure the current user is an admin."""
    if not current_user["is_admin"]:
        logger.error("The user doesn't have enough privileges")
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user


def get_current_active_admin(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Ensure the current user is an active admin."""
    user = crud.get_user(db, username=current_user["username"])
    if not user or not user.is_admin:
        logger.error("The user doesn't have enough privileges")
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user


def create_tokens_for_user(user: dict) -> dict:
    """Create both access and refresh tokens for a user."""
    access_token = create_access_token(user, ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_refresh_token(user, REFRESH_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_expires": ACCESS_TOKEN_EXPIRE_MINUTES,
        "token_type": "bearer",
        "is_admin": user["is_admin"],
    }


def decode_and_validate_token(token: str, secret_key: str, algorithm: str) -> dict:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=401, detail="Invalid token or expired token"
        ) from e


async def get_user_by_refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """Retrieve a user based on a refresh token."""
    payload = decode_and_validate_token(
        refresh_token, settings.refresh_secret_key, algorithm=ALGORITHM
    )
    username: str = payload.get("username")
    if username is None:
        raise HTTPException(status_code=401, detail="Token missing username")
    user = crud.get_user(db, username=username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def verify_access_token(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """Verify access token's validity."""
    payload = decode_and_validate_token(token, settings.secret_key, algorithm=ALGORITHM)
    username: str = payload.get("username")
    if username is None:
        raise HTTPException(status_code=401, detail="Token missing username")
    user = crud.get_user(db, username=username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"username": username, "message": "Token is valid"}
