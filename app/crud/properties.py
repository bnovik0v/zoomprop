""" CRUD operations for properties. """

import datetime
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from . import models, schemas


def get_property(db: Session, property_id: int) -> models.Property:
    """Get property

    Args:
    - db (Session): Database session
    - property_id (int): Property ID

    Returns:
    - models.Property: Property model
    """
    return (
        db.query(models.Property)
        .filter(models.Property.property_id == property_id)
        .first()
    )


def get_properties(
    db: Session, skip: int = 0, limit: int = 10
) -> list[models.Property]:
    """Get all properties or a limited number of properties

    Args:
    - db (Session): Database session
    - skip (int): Number of records to skip
    - limit (int): Number of records to return

    Returns:
    - list[models.Property]: List of Property models
    """
    return db.query(models.Property).offset(skip).limit(limit).all()


def create_property(
    db: Session, property_: schemas.PropertyCreate | dict
) -> models.Property:
    """Create a new property.

    Args:
    - db (Session): Database session
    - property_ (PropertyCreate | dict): Property data

    Returns:
    - models.Property: Property model
    """
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


def create_properties(db: Session, properties: list[schemas.PropertyCreate]):
    """Create multiple properties

    Args:
    - db (Session): Database session
    - properties (list[PropertyCreate]): List of PropertyCreate objects

    Returns:
    - None
    """
    db_properties = [
        models.Property(**property_.model_dump()) for property_ in properties
    ]
    db.bulk_save_objects(db_properties)
    db.commit()


def update_property(
    db: Session, property_id: int, property_: schemas.PropertyUpdate | dict
) -> models.Property:
    """Update a property

    Args:
    - db (Session): Database session
    - property_id (int): Property ID
    - property_ (PropertyUpdate | dict): Property data

    Returns:
    - models.Property: Property model
    """
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
    """Delete a property

    Args:
    - db (Session): Database session
    - property_id (int): Property ID

    Returns:
    - models.Property: Property model
    """
    db_property = (
        db.query(models.Property)
        .filter(models.Property.property_id == property_id)
        .first()
    )
    if db_property:
        db.delete(db_property)
        db.commit()
    return db_property


def apply_filters(
    query,
    price_min: float | None = None,
    price_max: float | None = None,
    bedrooms: int | None = None,
    bathrooms: float | None = None,
    city: str | None = None,
):
    """Apply filters to a query

    Args:
    - query: SQLAlchemy query
    - price_min (float): Minimum price
    - price_max (float): Maximum price
    - bedrooms (int): Number of bedrooms
    - bathrooms (int): Number of bathrooms
    - city (str): City

    Returns:
    - query: SQLAlchemy query
    """
    if price_min is not None:
        query = query.filter(models.Property.price >= price_min)
    if price_max is not None:
        query = query.filter(models.Property.price <= price_max)
    if bedrooms is not None:
        query = query.filter(models.Property.bedrooms == bedrooms)
    if bathrooms is not None:
        query = query.filter(models.Property.bathrooms == bathrooms)
    if city is not None:
        query = query.filter(models.Property.city == city)
    return query


def get_property_statistics(
    db: Session,
    price_min: float | None = None,
    price_max: float | None = None,
    bedrooms: int | None = None,
    bathrooms: float | None = None,
    city: str | None = None,
):
    """Get property statistics with optional filters.

    Args:
    - db (Session): Database session
    - price_min (float): Minimum price
    - price_max (float): Maximum price
    - bedrooms (int): Number of bedrooms
    - bathrooms (float): Number of bathrooms
    - city (str): City

    Returns:
    - dict: Property statistics
    """
    query = db.query(models.Property)
    query = apply_filters(query, price_min, price_max, bedrooms, bathrooms, city)

    avg_price = query.with_entities(func.avg(models.Property.price)).scalar()
    avg_price_per_sqft = query.with_entities(
        func.avg(models.Property.price / models.Property.square_feet)
    ).scalar()
    total_properties = query.with_entities(
        func.count(models.Property.property_id)
    ).scalar()

    # Calculate the median price
    count = query.with_entities(func.count(models.Property.property_id)).scalar()
    if count == 0:
        median_price = None
    else:
        if count % 2 == 1:
            median_price = (
                query.with_entities(models.Property.price)
                .order_by(models.Property.price)
                .offset(count // 2)
                .limit(1)
                .scalar()
            )
        else:
            median_price = (
                query.with_entities(func.avg(models.Property.price))
                .filter(
                    models.Property.price.in_(
                        query.with_entities(models.Property.price)
                        .order_by(models.Property.price)
                        .offset((count // 2) - 1)
                        .limit(2)
                    )
                )
                .scalar()
            )

    return {
        "average_price": avg_price,
        "median_price": median_price,
        "average_price_per_sqft": avg_price_per_sqft,
        "total_properties": total_properties,
    }


def filter_properties(
    db: Session,
    price_min: float | None = None,
    price_max: float | None = None,
    bedrooms: int | None = None,
    bathrooms: int | None = None,
    city: str | None = None,
    skip: int = 0,
    limit: int = 10,
) -> list[models.Property]:
    """Filter properties

    Args:
    - db (Session): Database session
    - price_min (float): Minimum price
    - price_max (float): Maximum price
    - bedrooms (int): Number of bedrooms
    - bathrooms (int): Number of bathrooms
    - city (str): City
    - skip (int): Number of records to skip
    - limit (int): Number of records to return

    Returns:
    - list[models.Property]: List of Property models
    """
    query = db.query(models.Property)
    query = apply_filters(query, price_min, price_max, bedrooms, bathrooms, city)
    return query.offset(skip).limit(limit).all()


def detect_price_outliers(
    db: Session,
    price_min: float | None = None,
    price_max: float | None = None,
    bedrooms: int | None = None,
    bathrooms: int | None = None,
    city: str | None = None,
    factor: float = 1.5,
    skip: int = 0,
    limit: int = 10,
) -> list[models.Property]:
    """Detect outliers in property prices using the IQR method with optional filters.

    Args:
    - db (Session): Database session
    - price_min (float): Minimum price
    - price_max (float): Maximum price
    - bedrooms (int): Number of bedrooms
    - bathrooms (int): Number of bathrooms
    - city (str): City
    - factor (float): IQR factor
    - skip (int): Number of records to skip
    - limit (int): Number of records to return

    Returns:
    - list[models.Property]: List of Property models
    """
    filtered_query = db.query(models.Property)
    filtered_query = apply_filters(
        filtered_query, price_min, price_max, bedrooms, bathrooms, city
    )

    prices = [
        property_.price
        for property_ in filtered_query.all()
        if property_.price is not None
    ]
    if not prices:
        return []

    q1 = np.percentile(prices, 25)
    q3 = np.percentile(prices, 75)
    iqr = q3 - q1
    lower_bound = q1 - factor * iqr
    upper_bound = q3 + factor * iqr

    outliers_query = filtered_query.filter(
        (models.Property.price < lower_bound) | (models.Property.price > upper_bound)
    )

    outliers = outliers_query.offset(skip).limit(limit).all()

    return outliers


def get_historical_insights(
    db: Session,
    start_date: datetime.datetime | None = None,
    end_date: datetime.datetime | None = None,
):
    """Get historical insights based on the DateListed column."""
    query = db.query(models.Property)
    if start_date:
        query = query.filter(models.Property.date_listed >= start_date)
    if end_date:
        query = query.filter(models.Property.date_listed <= end_date)

    insights = (
        query.with_entities(
            extract("year", models.Property.date_listed).label("year"),
            extract("month", models.Property.date_listed).label("month"),
            func.count(models.Property.property_id).label("count"),
            func.avg(models.Property.price).label("average_price"),
            func.avg(models.Property.square_feet).label("average_square_feet"),
        )
        .group_by("year", "month")
        .order_by("year", "month")
        .all()
    )

    result = [
        {
            "year": insight.year,
            "month": insight.month,
            "count": insight.count,
            "average_price": insight.average_price,
            "average_square_feet": insight.average_square_feet,
        }
        for insight in insights
    ]
    return result
