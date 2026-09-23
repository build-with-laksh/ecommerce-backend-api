import pytest

@pytest.mark.anyio
async def test_create(
    client,
    admin_token
):
    response = await client.post(
        '/products',
        json={
            "product_name":"Testing Product",
            "product_category":"Testing Category",
            "product_price":5000,
            "stock_quantity":500
        },
        headers={
            "Authorization" : f"Bearer {admin_token}"
        }
    )

    assert response.status_code == 200
    assert response.json()["product_name"] == "Testing Product"
    assert response.json()["product_category"] == "Testing Category"
    assert response.json()["product_price"] == 5000
    assert response.json()["stock_quantity"] == 500
    assert "id" in response.json()

@pytest.mark.anyio
async def test_get_products(
    client,
    product
):
    response = await client.get('/products')

    assert response.status_code == 200
    assert response.json()[0]["product_name"] == product["product_name"]
    assert response.json()[0]["product_category"] == product["product_category"]
    assert response.json()[0]["product_price"] == product["product_price"]
    assert response.json()[0]["stock_quantity"] == product["stock_quantity"]

@pytest.mark.anyio
async def test_get_product_by_id(
    client,
    product
):

    response = await client.get(
        f'/products/{product["id"]}',
    )

    assert response.status_code == 200
    assert "id" in response.json()
    assert "product_name" in response.json()
    assert "product_category" in response.json()
    assert "product_price" in response.json()
    assert "stock_quantity" in response.json()

@pytest.mark.anyio
async def test_product_patch(
    client,
    product,
    admin_token
):
    response = await client.patch(
        f'/products/{product["id"]}',
        json={
            "product_price":8000,
            "stock_quantity":800
        },
        headers={
            "Authorization" : f"Bearer {admin_token}"
        }
    )

    assert response.status_code == 200
    assert response.json()["product_name"] == "Testing Product 2"
    assert response.json()["product_category"] == "Testing Category"
    assert response.json()["product_price"] == 8000
    assert response.json()["stock_quantity"] == 800

@pytest.mark.anyio
async def test_delete_product(
    client,
    product,
    admin_token
):
    response = await client.delete(
        f"products/{product['id']}",
        headers={
            "Authorization" : f"Bearer {admin_token}"
        }
    )

    assert response.status_code == 200

