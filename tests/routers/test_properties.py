""" Tests for the properties router."""

import pytest
from fastapi.testclient import TestClient


def test_create_property(client: TestClient, auth_headers ):
    """Test creating a property."""
    property_data = {
        "property_id": 1,
        "address": "123 Main St",
        "city": "Springfield",
        "state": "IL",
        "zip_code": "62701",
        "price": 100000,
        "bedrooms": 3,
        "bathrooms": 2,
        "square_feet": 1500,
        "date_listed": "2021-01-01T00:00:00",
    }
    response = client.post("/api/properties/", json=property_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["address"] == property_data["address"]


def test_get_property_statistics(client: TestClient, auth_headers):
    """Test getting property statistics."""
    response = client.get("/api/properties/statistics/", headers=auth_headers)
    assert response.status_code == 200


def test_read_properties(client: TestClient, auth_headers):
    """Test reading properties."""
    response = client.get("/api/properties/", headers=auth_headers)
    assert response.status_code == 200


def test_update_property(client: TestClient, auth_headers):
    """Test updating a property."""
    property_update = {"bedrooms": 4}
    create_response = client.post(
        "/api/properties/",
        json={
            "property_id": 2,
            "address": "123 Main St",
            "city": "Springfield",
            "state": "IL",
            "zip_code": "62701",
            "price": 100000,
            "bedrooms": 3,
            "bathrooms": 2,
            "square_feet": 1500,
            "date_listed": "2021-01-01T00:00:00",
        },
        headers=auth_headers,
    )
    property_id = create_response.json()["property_id"]
    response = client.put(
        f"/api/properties/{property_id}/", json=property_update, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["bedrooms"] == property_update["bedrooms"]


def test_delete_property(client: TestClient, auth_headers):
    create_response = client.post(
        "/api/properties/",
        json={
            "property_id": 3,
            "address": "123 Main St",
            "city": "Springfield",
            "state": "IL",
            "zip_code": "62701",
            "price": 100000,
            "bedrooms": 3,
            "bathrooms": 2,
            "square_feet": 1500,
            "date_listed": "2021-01-01T00:00:00",
        },
        headers=auth_headers,
    )
    property_id = create_response.json()["property_id"]
    response = client.delete(f"/api/properties/{property_id}/", headers=auth_headers)
    assert response.status_code == 200
