from fastapi import FastAPI, Depends, HTTPException, status
import uvicorn
from sqlalchemy import select, text
from app.db import get_db
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import UserCreate, UserPublic, UserPrivate
from app.auth import hash_password, verify_hash_password
from app import models
from app.routers import users, products, cartitems

app = FastAPI()

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(products.router, prefix="/products", tags=["products"])
app.include_router(cartitems.router, prefix="/cart", tags=["cart"])

@app.get('/health')
async def home(db:Annotated[AsyncSession, Depends(get_db)]):
    try:    
        await db.execute(text("SELECT 1"))
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database Unavailable",
        ) from error
    return {"message":"ecommerce backend is running"}
