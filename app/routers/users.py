from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy import select, func
from app.db import get_db
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import UserCreate, UserPublic, UserPrivate
from app.auth import hash_password, verify_hash_password
from app import models

router = APIRouter()

@router.get("/{user_id}", response_model=UserPublic)
async def get_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):

    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "User Id Not Found"
        )

    return user


@router.post("/register", response_model=UserPrivate)
async def create_user(user:UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User).where(func.lower(models.User.username) == user.username.lower()))
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Username Already Exist"
        )
    result = await db.execute(select(models.User).where(models.User.email == user.email))
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Email Already Exists"
        )

    hash_pass = hash_password(user.password)

    new_user = models.User(
        username = user.username,
        email = user.email,
        hashed_password = hash_pass
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


