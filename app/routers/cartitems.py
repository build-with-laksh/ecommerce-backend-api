from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy import select, func
from app.db import get_db
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import CartItemCreate, CartItemPublic, CartUpdate
from app.auth import CurrentUser
from app import models
from datetime import timedelta, datetime, UTC

router = APIRouter()

@router.post('', response_model=CartItemPublic)
async def add_item_in_cart(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    product_data: CartItemCreate

):
    result = await db.execute(select(models.Product).where(models.Product.id == product_data.product_id))
    product = result.scalars().first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product Not Found"
        )

    if product.stock_quantity < product_data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Currently we have only {product.stock_quantity} stock please add with the lower quantity"
        )

    result = await db.execute(select(models.CartItem).where(models.CartItem.product_id == product_data.product_id, models.CartItem.user_id == current_user.id))
    cart_product = result.scalars().first()

    if cart_product:
        new_quantity = cart_product.quantity + product_data.quantity
        if new_quantity > product.stock_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Currently we have only {product.stock_quantity} stock please add with the lower quantity"
            )

        cart_product.quantity = new_quantity
        await db.commit()
        await db.refresh(cart_product)
        return cart_product

    new_product_in_cart = models.CartItem(
        user_id = current_user.id,
        product_id = product.id,
        quantity = product_data.quantity
    )

    db.add(new_product_in_cart)
    await db.commit()
    await db.refresh(new_product_in_cart)
    return new_product_in_cart


@router.get('', response_model=list[CartItemPublic])
async def get_cart_items(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(models.CartItem).where(models.CartItem.user_id == current_user.id))
    all_products = result.scalars().all()

    return all_products

@router.patch('/{cart_item_id}', response_model=CartItemPublic)
async def update_cart_by_cartid(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    cart_item_id: int,
    update_quantity: CartUpdate
):
    result = await db.execute(select(models.CartItem).where(models.CartItem.id == cart_item_id))
    cart_item = result.scalars().first()

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found with cartitem id"
        )

    if cart_item.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You're Not Authorized to update this cart item"
        )

    result = await db.execute(select(models.Product).where(models.Product.id == cart_item.product_id))
    product = result.scalars().first()

    new_quantity = update_quantity.quantity
    if new_quantity <= product.stock_quantity:
        cart_item.quantity = new_quantity
        await db.commit()
        await db.refresh(cart_item)
        return cart_item
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Currently we have only {product.stock_quantity} stock please add with the lower quantity"
        )

@router.delete('/{cart_item_id}')
async def delete_cart_item(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    cart_item_id: int
):
    result = await db.execute(
        select(
            models.CartItem
        ).where(
            models.CartItem.id == cart_item_id,
            models.CartItem.user_id == current_user.id
        )
    )

    cart_item = result.scalars().first()
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CartItem Not Found"
        )
    await db.delete(cart_item)
    await db.commit()
    return "Your Cart Item has been Deleted."
