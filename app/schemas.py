from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from app import models

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

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)

class CartItemPublic(CartItemCreate):
    id: int

class CartUpdate(BaseModel):
    quantity: int = Field(gt=0)

class OrderItemPublic(BaseModel):
    id: int
    product_id: int
    purchase_price: int
    quantity: int

class OrderPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    total_bill: int
    total_units: int
    status: str
    purchased_at: datetime
    order_items: OrderItemPublic 



