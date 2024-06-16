"""API endpoints for properties."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas
from app.auth import oauth2_scheme
from app.database import get_db


router = APIRouter(
    prefix="/api",
    tags=["Properties"],
)


@router.post("/properties/", response_model=schemas.Property)
def create_property(
    property_: schemas.PropertyCreate,
    db: Session = Depends(get_db),
    auth_token: str = Depends(oauth2_scheme),
):
    """Create a new property."""
    return crud.create_property(db=db, property_=property_)


@router.get("/properties/{property_id}", response_model=schemas.Property)
def read_property(
    property_id: int,
    db: Session = Depends(get_db),
    auth_token: str = Depends(oauth2_scheme),
):
    """Get a property by ID."""
    db_property = crud.get_property(db, property_id=property_id)
    if db_property is None:
        raise HTTPException(status_code=404, detail="Property not found")
    return db_property


@router.get("/properties/", response_model=list[schemas.Property])
def read_properties(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    auth_token: str = Depends(oauth2_scheme),
):
    """Get all properties or a limited number of properties."""
    properties = crud.get_properties(db, skip=skip, limit=limit)
    return properties


@router.put("/properties/{property_id}", response_model=schemas.Property)
def update_property(
    property_id: int,
    property_: schemas.PropertyUpdate,
    db: Session = Depends(get_db),
    auth_token: str = Depends(oauth2_scheme),
):
    """Update a property."""
    db_property = crud.get_property(db, property_id=property_id)
    if db_property is None:
        raise HTTPException(status_code=404, detail="Property not found")
    return crud.update_property(db=db, property_id=property_id, property_=property_)


@router.delete("/properties/{property_id}", response_model=schemas.Property)
def delete_property(
    property_id: int,
    db: Session = Depends(get_db),
    auth_token: str = Depends(oauth2_scheme),
):
    """Delete a property."""
    db_property = crud.get_property(db, property_id=property_id)
    if db_property is None:
        raise HTTPException(status_code=404, detail="Property not found")
    return crud.delete_property(db=db, property_id=property_id)
