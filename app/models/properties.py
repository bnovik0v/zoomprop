""" This module defines the SQLAlchemy model for the properties table. """

import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, True_
from app.database import Base


class Property(Base):
    """Property model."""

    __tablename__ = "properties"

    property_id = Column(Integer, primary_key=True, index=True)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    zip_code = Column(String, nullable=False)
    price = Column(Float, nullable=True)
    bedrooms = Column(Integer, nullable=True)
    bathrooms = Column(Float, nullable=True)
    square_feet = Column(Integer, nullable=True)
    date_listed = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    def __repr__(self):
        """Return string representation of the model."""
        return f"<Property(Address={self.address}, City={self.city}, State={self.state}, Price={self.price})>"
