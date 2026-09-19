from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy import select, func
from app.db import get_db
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import OrderItemPublic, OrderPublic
from app.auth import CurrentUser
from app import models
from datetime import timedelta, datetime, UTC

router = APIRouter()

@router.post("/checkout", response_model=OrderPublic)
async def checkout(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(models.CartItem).where(models.CartItem.user_id == current_user.id))
    cart_items = result.scalars().all()

    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No Products in your cart."
        )
    total_bill = 0
    total_units = 0
    for item in cart_items:
        result = await db.execute(select(models.Product).where(models.Product.id == item.product_id))
        product = result.scalars().first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail= f"Sorry, the Product (product_id: {item.product_id}) you want to order is now removed by the admin."
            )

        if product.stock_quantity < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The Product (product_id: {item.product_id}) you want to order is now lower in stock available units: {product.stock_quantity}"
            )
        total_bill += product.product_price * item.quantity
        total_units += item.quantity

    new_order = models.Order(
        user_id = current_user.id,
        total_bill = total_bill,
        total_units = total_units,
    )

    db.add(new_order)
    await db.flush()

    for item in cart_items:
        result = await db.execute(select(models.Product).where(models.Product.id == item.product_id))
        product = result.scalars().first()
        order_item_create = models.OrderItem(
            order_id = new_order.id,
            product_id = item.product_id,
            purchase_price = product.product_price,
            quantity = item.quantity,
        )
        product.stock_quantity -= item.quantity
        db.add(order_item_create)
        await db.delete(item)

    await db.commit()
    await db.refresh(new_order)
    return new_order

        
        

