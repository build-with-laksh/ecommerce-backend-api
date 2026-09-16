from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy import select, func
from app.db import get_db
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import UserCreate, UserPublic, UserPrivate, Token
from app.auth import (
    hash_password, 
    verify_hash_password, 
    create_access_token, 
    CurrentUser)

from app import models
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta, datetime, UTC
from app.config import settings

router = APIRouter()

@router.get('/me', response_model=UserPublic)
async def get_current_user(current_user: CurrentUser):
    return current_user

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

@router.post('/login', response_model=Token)
async def login_for_access_token(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(models.User).where(models.User.username == form.username))
    user = result.scalars().first()

    if not user or not verify_hash_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials Please Check and Try Again",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token({"sub":str(user.id)}, expires_delta=access_token_expires)

    return Token(
        access_token=access_token,
        token_type="bearer"
    )




