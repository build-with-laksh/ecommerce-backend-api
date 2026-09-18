from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy import select, func
from app.db import get_db
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import ProductCreate, ProductPublic, ProductUpdate
from app.auth import admin_check, CurrentUser
from app import models
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta, datetime, UTC
from app.config import settings

router = APIRouter()

@router.post("", response_model=ProductPublic)
async def create_products(
    admin: Annotated[models.User, Depends(admin_check)], 
    product: ProductCreate, 
    db: Annotated[AsyncSession, Depends(get_db)]
):

    new_product = models.Product(
        product_name = product.product_name,
        product_category = product.product_category,
        product_price = product.product_price,
        stock_quantity = product.stock_quantity
    )
    
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product

@router.get('', response_model=list[ProductPublic])
async def get_all_products(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    results = await db.execute(select(models.Product))
    products = results.scalars().all()

    return products

@router.get('/{product_id}', response_model=ProductPublic)
async def get_product(
    product_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(models.Product).where(models.Product.id == product_id))
    product = result.scalars().first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product Not Found"
        )

    return product

@router.patch('/{product_id}', response_model=ProductPublic)
async def update_products_partial(
   admin_user: Annotated[models.User, Depends(admin_check)],
   db: Annotated[AsyncSession, Depends(get_db)],
   product_id: int,
   product_data: ProductUpdate
):
    result = await db.execute(select(models.Product).where(models.Product.id == product_id))
    product = result.scalars().first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product Not Found"
        )

    if product_data.product_name is not None:
        product.product_name = product_data.product_name
    if product_data.product_category is not None:
        product.product_category = product_data.product_category
    if product_data.stock_quantity is not None:
        product.stock_quantity = product_data.stock_quantity
    if product_data.product_price is not None:
        product.product_price = product_data.product_price

    await db.commit()
    await db.refresh(product)
    return product

@router.delete("/{product_id}")
async def delete_product(
    admin_user: Annotated[models.User, Depends(admin_check)],
    db: Annotated[AsyncSession, Depends(get_db)],
    product_id: int
):
  
    result = await db.execute(select(models.Product).where(models.Product.id == product_id))
    product = result.scalars().first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product Not Found"
        )

    await db.delete(product)
    await db.commit()

    return "Your Product Has Been Deleted"
    
    