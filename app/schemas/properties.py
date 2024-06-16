""" This module defines the Pydantic schema for the properties table. """

from datetime import datetime
from pydantic import BaseModel


class PropertyBase(BaseModel):
    """Property base model."""

    property_id: int
    address: str
    city: str
    state: str
    zip_code: str
    price: float | None = None
    bedrooms: int | None = None
    bathrooms: float | None = None
    square_feet: int | None = None
    date_listed: datetime | None = None


class PropertyCreate(PropertyBase):
    """Property create model."""


class PropertyUpdate(PropertyBase):
    """Property update model."""


class Property(PropertyBase):
    """Property model."""

    class Config:
        """Config."""

        from_attributes = True


class PropertyStatistics(BaseModel):
    """Property statistics model."""

    average_price: float | None = None
    median_price: float | None = None
    average_price_per_sqft: float | None = None
    total_properties: int | None = None


class PropertyHistoricalInsight(BaseModel):
    """Historical insight model."""

    year: int
    month: int
    count: int
    average_price: float
    average_square_feet: float

    class Config:
        """Config."""

        from_attributes = True
