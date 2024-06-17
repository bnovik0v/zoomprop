# Zoomprop Senior Python Engineer Take Home Assessment

## Overview
This project is a property management API built with FastAPI. It allows users to create, read, update, and delete property records, as well as fetch various statistics and visualizations about the properties. The project is containerized using Docker and uses SQLite as the database.

## Solution Overview
The solution involves building a RESTful API for managing property data, which includes endpoints for creating, reading, updating, and deleting properties, as well as generating statistics and visualizations based on the property data. The API is secured with token-based authentication.

Key components include:
- **CRUD operations** for properties.
- **Statistical endpoints** to fetch property statistics.
- **Data visualization** endpoints that return plots as base64 encoded images.
- **CSV upload** endpoint for bulk property data import.

## Setup and Run Instructions

### Prerequisites
- Docker
- Python 3.9+
- `pip` for installing Python packages

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/bnovik0v/zoomprop
   cd zoomprop
   ```

2. Create the `.env` file:
   ```bash
   touch .env
   ```

3. Add the following environment variables to the `.env` file:
   ```env
   GUNICORN_WORKERS=2
   SQLITE_DB=./database/database.db
   SECRET_KEY=sahdhskADHS341
   REFRESH_SECRET_KEY=1236213SAGDGhgdAGSDgg
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=password
   ADMIN_EMAIL=admin@mail.com
   ```

4. Build and run the Docker container:
   ```bash
   docker-compose up --build
   ```

5. Populate the database with test data:
   ```bash
   sudo apt-get install jq
   chmod +x ./scripts/upload_test_data.sh
   ./scripts/upload_test_data.sh
   ```

   Alternatively, you can use the following endpoint to upload the CSV file:
   ```http
   POST /api/properties/upload/csv
   ```

### Running Tests
1. Install pytest if you haven't already:
   ```bash
   pip install pytest
   ```

2. Run the tests:
   ```bash
   pytest
   ```

## API Endpoints

### Create a property
- **Endpoint**: `POST /api/properties/`
- **Description**: Create a new property record.
- **Request Body**:
  ```json
  {
    "property_id": 1,
    "address": "123 Main St",
    "city": "Anytown",
    "state": "CA",
    "zip_code": "12345",
    "price": 250000.0,
    "bedrooms": 3,
    "bathrooms": 2.0,
    "square_feet": 1500,
    "date_listed": "2023-01-01T00:00:00"
  }
  ```
- **Response**: `Property` schema.

### Get property statistics
- **Endpoint**: `GET /api/properties/statistics/`
- **Description**: Fetch statistics about properties.
- **Query Parameters**:
  - `price_min` (float, optional): Minimum price filter.
  - `price_max` (float, optional): Maximum price filter.
  - `bedrooms` (int, optional): Number of bedrooms filter.
  - `bathrooms` (int, optional): Number of bathrooms filter.
  - `city` (string, optional): City filter.
- **Response**: 
  ```json
  {
    "average_price": 300000.0,
    "median_price": 280000.0,
    "average_price_per_sqft": 200.0,
    "total_properties": 100
  }
  ```

### Read properties
- **Endpoint**: `GET /api/properties/`
- **Description**: Retrieve a list of properties.
- **Query Parameters**:
  - `price_min` (float, optional): Minimum price filter.
  - `price_max` (float, optional): Maximum price filter.
  - `bedrooms` (int, optional): Number of bedrooms filter.
  - `bathrooms` (int, optional): Number of bathrooms filter.
  - `city` (string, optional): City filter.
  - `skip` (int, default=0): Number of records to skip.
  - `limit` (int, default=10): Number of records to return.
- **Response**: List of `Property` schema.
  ```json
  [
    {
      "property_id": 1,
      "address": "123 Main St",
      "city": "Anytown",
      "state": "CA",
      "zip_code": "12345",
      "price": 250000.0,
      "bedrooms": 3,
      "bathrooms": 2.0,
      "square_feet": 1500,
      "date_listed": "2023-01-01T00:00:00"
    }
  ]
  ```

### Update a property
- **Endpoint**: `PUT /api/properties/{property_id}/`
- **Description**: Update an existing property record.
- **Path Parameter**: `property_id` (int): ID of the property to update.
- **Request Body**:
  ```json
  {
    "address": "456 Elm St",
    "city": "New City",
    "state": "NY",
    "zip_code": "54321",
    "price": 300000.0,
    "bedrooms": 4,
    "bathrooms": 3.0,
    "square_feet": 2000,
    "date_listed": "2023-02-01T00:00:00"
  }
  ```
- **Response**: Updated `Property` schema.

### Delete a property
- **Endpoint**: `DELETE /api/properties/{property_id}/`
- **Description**: Delete a property record.
- **Path Parameter**: `property_id` (int): ID of the property to delete.
- **Response**: Deleted `Property` schema.

### Upload properties from CSV
- **Endpoint**: `POST /api/properties/upload/csv/`
- **Description**: Upload multiple properties from a CSV file.
- **Form Data**: `file` (UploadFile): CSV file containing property data.
- **Response**: Success message.
  ```json
  {
    "status": "success",
    "message": "Properties uploaded successfully"
  }
  ```

### Get price distribution plot
- **Endpoint**: `GET /api/properties/plot/price_distribution/`
- **Description**: Get the distribution of property prices as a base64 PNG image.
- **Response**: JSON containing base64 encoded PNG image.
  ```json
  {
    "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
  }
  ```

### Get bedrooms distribution plot
- **Endpoint**: `GET /api/properties/plot/bedrooms_distribution/`
- **Description**: Get the distribution of properties by number of bedrooms as a base64 PNG image.
- **Response**: JSON containing base64 encoded PNG image.
  ```json
  {
    "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
  }
  ```

### Get price outliers
- **Endpoint**: `GET /api/properties/outliers/`
- **Description**: Retrieve properties with outlier prices.
- **Query Parameters**:
  - `price_min` (float, optional): Minimum price filter.
  - `price_max` (float, optional): Maximum price filter.
  - `bedrooms` (int, optional): Number of bedrooms filter.
  - `bathrooms` (int, optional): Number of bathrooms filter.
  - `city` (string, optional): City filter.
  - `factor` (float, default=1.5): Outlier detection factor.
  - `skip` (int, default=0): Number of records to skip.
  - `limit` (int, default=10): Number of records to return.
- **Response**: List of `Property` schema.
  ```json
  [
    {
      "property_id": 1,
      "address": "123 Main St",
      "city": "Anytown",
      "state": "CA",
      "zip_code": "12345",
      "price": 250000.0,
      "bedrooms": 3,
      "bathrooms": 2.0,
      "square_feet": 1500,
      "date_listed": "2023-01-01T00:00:00"
    }
  ]
  ```

### Get historical insights
- **Endpoint**: `GET /api/properties/insights/`
- **Description**: Get historical insights based on the DateListed column.
- **Query Parameters**:
  - `start_date` (datetime, optional): Start date filter.
  - `end_date` (datetime, optional): End date filter.
- **Response**: List of `PropertyHistoricalInsight` schema.
  ```json
  [
    {
      "year": 2023,
      "month": 1,
      "count": 10,
      "average_price": 250000.0,
      "average_square_feet": 1500
    }
  ]
  ```

### Read

 a property by ID
- **Endpoint**: `GET /api/properties/{property_id}/`
- **Description**: Get a property by its ID.
- **Path Parameter**: `property_id` (int): ID of the property to retrieve.
- **Response**: `Property` schema.
  ```json
  {
    "property_id": 1,
    "address": "123 Main St",
    "city": "Anytown",
    "state": "CA",
    "zip_code": "12345",
    "price": 250000.0,
    "bedrooms": 3,
    "bathrooms": 2.0,
    "square_feet": 1500,
    "date_listed": "2023-01-01T00:00:00"
  }
  ```

## Data Visualization

The application provides endpoints to generate visualizations of the property data. The visualizations are generated using Matplotlib and returned as base64 encoded PNG images. 

### Example Visualizations

#### Price Distribution
The `/api/properties/plot/price_distribution/` endpoint generates a histogram of property prices, allowing users to see the distribution of property prices in the dataset.

#### Bedrooms Distribution
The `/api/properties/plot/bedrooms_distribution/` endpoint generates a histogram of properties by the number of bedrooms, providing insights into the distribution of bedroom counts in the dataset.

## Running Tests
1. Install pytest if you haven't already:
   ```bash
   pip install pytest
   ```

2. Run the tests:
   ```bash
   pytest
   ```
