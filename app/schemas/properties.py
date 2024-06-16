""" This module defines the Pydantic schema for the properties table. """

from datetime import datetime
from pydantic import BaseModel


class PropertyBase(BaseModel):
    """Property base model."""

    address: str
    city: str
    state: str
    zip_code: str
    price: float
    bedrooms: int
    bathrooms: int
    square_feet: int


class PropertyCreate(PropertyBase):
    """Property create model."""


class PropertyUpdate(PropertyBase):
    """Property update model."""


class Property(PropertyBase):
    """Property model."""

    property_id: int
    date_listed: datetime

    class Config:
        """Config."""

        from_attributes = True
