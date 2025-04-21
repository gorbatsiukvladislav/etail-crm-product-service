import pytest
from app.schemas.product import CategoryCreate, ProductCreate

@pytest.mark.asyncio
async def test_create_category(client):
    category_data = {
        "name": "Electronics",
        "description": "Electronic devices and accessories"
    }
    
    response = client.post("/api/v1/products/categories/", json=category_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == category_data["name"]
    assert data["description"] == category_data["description"]
    assert "id" in data

@pytest.mark.asyncio
async def test_create_product(client, mock_rabbitmq):
    # First create a category
    category_data = {
        "name": "Electronics",
        "description": "Electronic devices"
    }
    category_response = client.post("/api/v1/products/categories/", json=category_data)
    category_id = category_response.json()["id"]
    
    # Then create a product
    product_data = {
        "name": "Smartphone",
        "description": "Latest model",
        "sku": "PHONE-001",
        "price": 999.99,
        "quantity": 10,
        "category_id": category_id,
        "is_active": True
    }
    
    response = client.post("/api/v1/products/products/", json=product_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == product_data["name"]
    assert data["sku"] == product_data["sku"]
    assert data["price"] == product_data["price"]
    assert "id" in data

@pytest.mark.asyncio
async def test_get_product_with_cache(client, redis_mock):
    # Create category and product first
    category = client.post("/api/v1/products/categories/", 
                         json={"name": "Test Category"}).json()
    
    product_data = {
        "name": "Test Product",
        "sku": "TEST-001",
        "price": 100.0,
        "quantity": 5,
        "category_id": category["id"],
    }
    created_product = client.post("/api/v1/products/products/", 
                                json=product_data).json()
    
    # First request - should cache the result
    response1 = client.get(f"/api/v1/products/products/{created_product['id']}")
    assert response1.status_code == 200
    
    # Second request - should use cache
    response2 = client.get(f"/api/v1/products/products/{created_product['id']}")
    assert response2.status_code == 200
    
    # Both responses should be identical
    assert response1.json() == response2.json()

@pytest.mark.asyncio
async def test_update_product(client, mock_rabbitmq, redis_mock):
    # Create category and product
    category = client.post("/api/v1/products/categories/", 
                         json={"name": "Test Category"}).json()
    
    product_data = {
        "name": "Original Name",
        "sku": "TEST-001",
        "price": 100.0,
        "quantity": 5,
        "category_id": category["id"],
    }
    created_product = client.post("/api/v1/products/products/", 
                                json=product_data).json()
    
    # Update product
    update_data = dict(product_data)
    update_data["name"] = "Updated Name"
    update_data["price"] = 150.0
    
    response = client.put(
        f"/api/v1/products/products/{created_product['id']}", 
        json=update_data
    )
    assert response.status_code == 200
    
    updated_product = response.json()
    assert updated_product["name"] == "Updated Name"
    assert updated_product["price"] == 150.0