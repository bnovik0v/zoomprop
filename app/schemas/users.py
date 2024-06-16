"""User schemas."""

from pydantic import BaseModel


class UserBase(BaseModel):
    """User base model."""

    username: str
    email: str


class UserCreate(UserBase):
    """User create model."""

    password: str
    is_admin: bool = False


class UserUpdate(UserBase):
    """User update model."""

    password: str
    is_admin: bool = False


class User(UserBase):
    """User model."""

    id: int
    is_admin: bool

    class Config:
        """Config."""

        from_attributes = True
