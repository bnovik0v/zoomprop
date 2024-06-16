"""Utility functions for generating visualizations of property data."""

import io
import base64
import matplotlib.pyplot as plt
from sqlalchemy.orm import Session
from app.models import Property


def plot_to_image(plt):
    """Convert a Matplotlib plot to a PNG image and return it as a base64 string."""
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close()
    return img_base64


def plot_price_distribution(db: Session):
    """Generate a histogram of property prices."""
    properties = db.query(Property.price).all()
    prices = [property.price for property in properties if property.price is not None]

    plt.figure(figsize=(10, 6))
    plt.hist(prices, bins=50, edgecolor="black")
    plt.title("Distribution of Property Prices")
    plt.xlabel("Price")
    plt.ylabel("Number of Properties")

    return plot_to_image(plt)


def plot_bedrooms_distribution(db: Session):
    """Generate a histogram of properties by number of bedrooms."""
    properties = db.query(Property.bedrooms).all()
    bedrooms = [
        property.bedrooms for property in properties if property.bedrooms is not None
    ]

    plt.figure(figsize=(10, 6))
    plt.hist(bedrooms, bins=range(1, 10), edgecolor="black", align="left")
    plt.title("Distribution of Properties by Number of Bedrooms")
    plt.xlabel("Number of Bedrooms")
    plt.ylabel("Number of Properties")

    return plot_to_image(plt)
