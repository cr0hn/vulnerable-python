"""
SQLAlchemy models for ByteBazaar.

Teaching notes live next to the risky fields and call sites (VULN: / SAFE:).
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    # VULN (A04): passwords stored with a fast hash is better than plaintext, but
    # we still keep a weak pattern in seed docs. SAFE: Argon2id / scrypt via a
    # purpose-built password hasher, never roll your own.
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    # VULN (A06 mass assignment): `role` is a persistence field the client must
    # never be allowed to set. SAFE: ignore client-supplied role; set server-side.
    role: Mapped[str] = mapped_column(String(32), default="customer")
    display_name: Mapped[str] = mapped_column(String(120), default="")

    orders: Mapped[list["Order"]] = relationship(back_populates="user")
    reviews: Mapped[list["Review"]] = relationship(back_populates="user")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    image: Mapped[str] = mapped_column(String(255), default="")
    category: Mapped[str] = mapped_column(String(80), default="merch")
    stock: Mapped[int] = mapped_column(Integer, default=50)

    reviews: Mapped[list["Review"]] = relationship(back_populates="product")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    total_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="paid")
    shipping_name: Mapped[str] = mapped_column(String(200), default="")
    shipping_address: Mapped[str] = mapped_column(Text, default="")
    # VULN (A04): card last4 + brand would be enough; we also keep a lab-only
    # full_pan field so students can see sensitive data at rest after checkout.
    # SAFE: tokenize with a PSP; never store PAN/CVV.
    card_last4: Mapped[str] = mapped_column(String(4), default="")
    card_pan_lab_only: Mapped[str] = mapped_column(String(32), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit_price_cents: Mapped[int] = mapped_column(Integer, nullable=False)

    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship()


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, default=5)
    # VULN (A05 XSS): body is rendered with |safe in the template.
    # SAFE: store as text, escape on output (Jinja default), or sanitize HTML.
    body: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    product: Mapped["Product"] = relationship(back_populates="reviews")
    user: Mapped["User"] = relationship(back_populates="reviews")


class PaymentAttempt(Base):
    """Lab table: shows what a careless checkout wrote to the database."""

    __tablename__ = "payment_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    # VULN (A04): full PAN + CVV persisted. SAFE: never store these.
    pan: Mapped[str] = mapped_column(String(32), default="")
    cvv: Mapped[str] = mapped_column(String(8), default="")
    amount_cents: Mapped[int] = mapped_column(Integer, default=0)
    accepted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
