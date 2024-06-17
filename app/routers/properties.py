"""API endpoints for properties."""

import logging
from io import StringIO
import datetime
import csv
from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from sqlalchemy.orm import Session
from app import crud, schemas, models
from app.auth import oauth2_scheme
from app.database import get_db
from app.services.visualization import (
    plot_price_distribution,
    plot_bedrooms_distribution,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api",
    tags=["Properties"],
)


@router.post("/properties/", response_model=schemas.Property)
async def create_property(
    property_: schemas.PropertyCreate,
    db: Session = Depends(get_db),
    auth_token: str = Depends(oauth2_scheme),
):
    """Create a new property."""
    logger.info("Creating property %s", property_)
    return crud.create_property(db=db, property_=property_)


@router.get("/properties/statistics/", response_model=schemas.PropertyStatistics)
async def get_property_statistics(
    price_min: float | None = Query(None, ge=0),
    price_max: float | None = Query(None, ge=0),
    bedrooms: int | None = Query(None, ge=0),
    bathrooms: int | None = Query(None, ge=0),
    city: str | None = Query(None),
    db: Session = Depends(get_db),
    auth_token: str = Depends(oauth2_scheme),
):
    """Get property statistics."""
    logger.info(
        "Getting property statistics with filters price_min=%s, price_max=%s, bedrooms=%s, bathrooms=%s, city=%s",
        price_min,
        price_max,
        bedrooms,
        bathrooms,
        city,
    )
    statistics = crud.get_property_statistics(
        db,
        price_min=price_min,
        price_max=price_max,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        city=city,
    )
    return statistics


@router.get("/properties/", response_model=list[schemas.Property])
async def read_properties(
    price_min: float | None = Query(None, ge=0),
    price_max: float | None = Query(None, ge=0),
    bedrooms: int | None = Query(None, ge=0),
    bathrooms: int | None = Query(None, ge=0),
    city: str | None = Query(None),
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    auth_token: str = Depends(oauth2_scheme),
):
    """Read properties."""
    logger.info(
        "Reading properties with filters price_min=%s, price_max=%s, bedrooms=%s, bathrooms=%s, city=%s",
        price_min,
        price_max,
        bedrooms,
        bathrooms,
        city,
    )
    properties = crud.filter_properties(
        db,
        price_min=price_min,
        price_max=price_max,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        city=city,
        skip=skip,
        limit=limit,
    )
    return properties


@router.put("/properties/{property_id}/", response_model=schemas.Property)
async def update_property(
    property_id: int,
    property_: schemas.PropertyUpdate,
    db: Session = Depends(get_db),
    auth_token: str = Depends(oauth2_scheme),
):
    """Update a property."""
    logger.info("Updating property %s with data %s", property_id, property_)
    db_property = crud.get_property(db, property_id=property_id)
    if db_property is None:
        logger.error("Property %s not found", property_id)
        raise HTTPException(status_code=404, detail="Property not found")
    return crud.update_property(db=db, property_id=property_id, property_=property_)


@router.delete("/properties/{property_id}/", response_model=schemas.Property)
async def delete_property(
    property_id: int,
    db: Session = Depends(get_db),
    auth_token: str = Depends(oauth2_scheme),
):
    """Delete a property."""
    logger.info("Deleting property %s", property_id)
    db_property = crud.get_property(db, property_id=property_id)
    if db_property is None:
        logger.error("Property %s not found", property_id)
        raise HTTPException(status_code=404, detail="Property not found")
    return crud.delete_property(db=db, property_id=property_id)


def parse_date(date_str: str) -> datetime.datetime | None:
    """Parse date string into datetime object."""
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Date format for {date_str} not supported.")


@router.post("/properties/upload/csv/")
def upload_properties_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    auth_token: str = Depends(oauth2_scheme),
):
    """Upload properties from a CSV file."""
    logger.info("Uploading properties from CSV file %s", file.filename)
    if not file.filename.endswith(".csv"):
        logger.error("File format not supported. Please upload a CSV file.")
        raise HTTPException(
            status_code=400,
            detail="File format not supported. Please upload a CSV file.",
        )

    content = file.file.read().decode("utf-8")
    csv_reader = csv.DictReader(StringIO(content))

    existing_property_ids = set(db.query(models.Property.property_id).all())
    properties = []
    for row in csv_reader:
        property_id = int(row["propertyid"])
        if property_id in existing_property_ids:
            logger.warning(
                "Property ID %s already exists. Skipping.", row["propertyid"]
            )
            continue
        property_ = schemas.PropertyCreate(
            property_id=int(row["propertyid"]),
            address=row["address"],
            city=row["city"],
            state=row["state"],
            zip_code=row["zipcode"],
            price=float(row["price"]) if row["price"] else None,
            bedrooms=int(row["bedrooms"]) if row["bedrooms"] else None,
            bathrooms=float(row["bathrooms"]) if row["bathrooms"] else None,
            square_feet=int(row["squarefeet"]) if row["squarefeet"] else None,
            date_listed=(parse_date(row["datelisted"]) if row["datelisted"] else None),
        )
        properties.append(property_)
        existing_property_ids.add(property_id)

    if properties:
        crud.create_properties(db=db, properties=properties)
    else:
        logger.warning("No new properties to upload")
        return {"status": "success", "message": "No new properties to upload"}

    return {"status": "success", "message": "Properties uploaded successfully"}


@router.get("/properties/plot/price_distribution/")
async def get_price_distribution(
    db: Session = Depends(get_db),
    auth_token: str = Depends(oauth2_scheme),
):
    """Get the distribution of property prices as a base64 PNG image."""
    logger.info("Getting property price distribution")
    img_base64 = plot_price_distribution(db)
    return {"image": img_base64}


@router.get("/properties/plot/bedrooms_distribution/")
async def get_bedrooms_distribution(
    db: Session = Depends(get_db),
    auth_token: str = Depends(oauth2_scheme),
):
    """Get the distribution of properties by number of bedrooms as a base64 PNG image."""
    logger.info("Getting property bedrooms distribution")
    img_base64 = plot_bedrooms_distribution(db)
    return {"image": img_base64}


@router.get("/properties/outliers/", response_model=list[schemas.Property])
async def get_price_outliers(
    price_min: float | None = Query(None, ge=0),
    price_max: float | None = Query(None, ge=0),
    bedrooms: int | None = Query(None, ge=0),
    bathrooms: int | None = Query(None, ge=0),
    city: str | None = Query(None),
    factor: float = 1.5,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    auth_token: str = Depends(oauth2_scheme),
):
    """Get properties with outlier prices."""
    logger.info(
        "Getting price outliers with filters price_min=%s, price_max=%s, bedrooms=%s, bathrooms=%s, city=%s, factor=%s",
        price_min,
        price_max,
        bedrooms,
        bathrooms,
        city,
        factor,
    )
    outliers = crud.detect_price_outliers(
        db,
        price_min=price_min,
        price_max=price_max,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        city=city,
        factor=factor,
        skip=skip,
        limit=limit,
    )
    return outliers


@router.get(
    "/properties/insights/", response_model=list[schemas.PropertyHistoricalInsight]
)
async def get_historical_insights(
    start_date: datetime.datetime | None = Query(None),
    end_date: datetime.datetime | None = Query(None),
    db: Session = Depends(get_db),
    auth_token: str = Depends(oauth2_scheme),
):
    """Get historical insights based on the DateListed column."""
    logger.info(
        "Getting historical insights with filters start_date=%s, end_date=%s",
        start_date,
        end_date,
    )
    insights = crud.get_historical_insights(
        db, start_date=start_date, end_date=end_date
    )
    return insights


@router.get("/properties/{property_id}/", response_model=schemas.Property)
async def read_property(
    property_id: int,
    db: Session = Depends(get_db),
    auth_token: str = Depends(oauth2_scheme),
):
    """Get a property by ID."""
    logger.info("Getting property %s", property_id)
    db_property = crud.get_property(db, property_id=property_id)
    if db_property is None:
        logger.error("Property %s not found", property_id)
        raise HTTPException(status_code=404, detail="Property not found")
    return db_property
