"""Tests for the CRUD operations for properties."""

from sqlalchemy.orm import Session
from app import crud, schemas


def test_create_property(db: Session):
    """Test creating a property."""
    property_data = schemas.PropertyCreate(
        property_id=1,
        address="123 Main St",
        city="Springfield",
        state="IL",
        zip_code="62701",
        price=100000,
        bedrooms=3,
        bathrooms=2,
        square_feet=1500,
        date_listed="2021-01-01T00:00:00",
    )
    property_ = crud.create_property(db, property_data)
    assert property_ is not None


def test_get_property(db: Session):
    """Test getting a property."""
    property_ = crud.get_property(db, 1)
    assert property_ is not None


def test_update_property(db: Session):
    """Test updating a property."""
    update_data = {"price": 120000}
    property_ = crud.update_property(db, 1, update_data)
    assert property_.price == 120000


def test_delete_property(db: Session):
    property_ = crud.delete_property(db, 1)
    assert property_ is not None
