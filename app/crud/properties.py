""" CRUD operations for properties. """

from sqlalchemy.orm import Session
from . import models, schemas


def get_property(db: Session, property_id: int) -> models.Property:
    """Get property."""
    return (
        db.query(models.Property)
        .filter(models.Property.property_id == property_id)
        .first()
    )


def get_properties(
    db: Session, skip: int = 0, limit: int = 10
) -> list[models.Property]:
    """Get all properties or a limited number of properties"""
    return db.query(models.Property).offset(skip).limit(limit).all()


def create_property(
    db: Session, property_: schemas.PropertyCreate | dict
) -> models.Property:
    """Create a new property."""
    if isinstance(property_, dict):
        data = property_
    elif isinstance(property_, schemas.PropertyCreate):
        data = property_.model_dump()
    else:
        raise TypeError("property must be a dict or a PropertyCreate object")

    db_property = models.Property(**data)
    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    return db_property


def update_property(
    db: Session, property_id: int, property_: schemas.PropertyUpdate | dict
) -> models.Property:
    """Update a property."""
    db_property = (
        db.query(models.Property)
        .filter(models.Property.property_id == property_id)
        .first()
    )
    if db_property:
        if isinstance(property_, dict):
            data = property_
        elif isinstance(property_, schemas.PropertyUpdate):
            data = property_.model_dump(exclude_unset=True)
        else:
            raise TypeError("property must be a dict or a PropertyUpdate object")

        for key, value in data.items():
            setattr(db_property, key, value)
        db.commit()
        db.refresh(db_property)
    return db_property


def delete_property(db: Session, property_id: int) -> models.Property:
    """Delete a property."""
    db_property = (
        db.query(models.Property)
        .filter(models.Property.property_id == property_id)
        .first()
    )
    if db_property:
        db.delete(db_property)
        db.commit()
    return db_property
