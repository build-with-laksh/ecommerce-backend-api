import pytest

@pytest.mark.anyio
async def test_add_item_in_cart(
    client,
    token,
    product
):
    response = await client.post(
        '/cart',
        json={
            "product_id":product["id"],
            "quantity":100
        },
        headers={
            "Authorization" : f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["product_id"] == product["id"]

@pytest.mark.anyio
async def test_get_cart(
    client,
    token,
    cart_item
):
    response = await client.get(
        "/cart",
        headers={
            "Authorization" : f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert response.json()[0]['product_id'] == cart_item["product_id"]
    assert response.json()[0]["quantity"] == cart_item["quantity"]

@pytest.mark.anyio
async def test_update_cart(
    client,
    token,
    cart_item,
):
    response = await client.patch(
       f"cart/{cart_item["id"]}",
       json={
           "quantity":200
       },
       headers={
           "Authorization" : f"Bearer {token}"
       }
    )

    assert response.status_code == 200
    assert response.json()["product_id"] == cart_item["product_id"]
    assert response.json()["quantity"] == 200

@pytest.mark.anyio
async def test_delete_cart(
    client,
    token,
    cart_item
):
    response = await client.delete(
        f"/cart/{cart_item["id"]}",
        headers={
            "Authorization" : f"Bearer {token}"
        }
    )

    assert response.status_code == 200