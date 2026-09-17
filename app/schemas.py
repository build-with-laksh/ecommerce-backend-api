from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserPublic(BaseModel):
    id: int
    username: str

class UserPrivate(UserPublic):
    email: EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str

class ProductCreate(BaseModel):
    product_name: str = Field(min_length=1)
    product_category: str = Field(min_length=1)
    product_price: int =  Field(gt=0)
    stock_quantity: int = Field(ge=0)

class ProductPublic(ProductCreate):
    id: int

class ProductUpdate(BaseModel):
    product_name: str | None = Field(default=None, min_length=1)
    product_category: str | None = Field(default=None, min_length=1)
    product_price: int | None =  Field(default=None, gt=0)
    stock_quantity: int | None = Field(default=None, ge=0)

