from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey
from db import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    username:Mapped[str] = mapped_column(String, nullable=False, unique=True)
    email:Mapped[str] = mapped_column(String, nullable=False, unique=True)
    hashed_password:Mapped[str] = mapped_column(String, nullable=False)
    is_active:Mapped[bool] = mapped_column(
        Boolean,
        default=True, 
        nullable=False
    )
    cart_items:Mapped[list["CartItem"]] = relationship(
        back_populates="user"
    )

class CartItem(Base):
    __tablename__ = "cartitems"

    id:Mapped[int] = mapped_column(
        Integer, 
        primary_key=True
    )
    
    user_id:Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    product_id:Mapped[int] = mapped_column(
        ForeignKey("products.id")
    )

    quantity:Mapped[int] = mapped_column(
        Integer, 
        default=1
    )

    added_at:Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.now
    )

    user:Mapped["User"] = relationship(
        back_populates="cart_items"
    )

    product:Mapped["Product"] = relationship(
        back_populates="cart_items"
    )

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    product_name: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    product_category: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    product_price: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    stock_quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    added_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now
    )

    cart_items: Mapped[list["CartItem"]] = relationship(
        back_populates="product"
    )