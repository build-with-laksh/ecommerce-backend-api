import pytest

@pytest.mark.anyio
async def test_checkout(
    client,
    token,
    cart_item
):
    response = await client.post(
        "/order/checkout",
        headers={
            "Authorization" : f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert "id" in response.json()
    assert "total_bill" in response.json()
    assert "total_units" in response.json()
    assert "status" in response.json()
    assert "purchased_at" in response.json()
    assert "order_items" in response.json() 
