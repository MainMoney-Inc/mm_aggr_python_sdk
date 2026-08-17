"""SQLite models for the FastAPI mini-shop."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "db.sqlite3"
INITIAL_DB = ROOT / "data" / "initial.sqlite3"

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sku: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(String, default="")
    price: Mapped[str] = mapped_column(String(32))
    currency: Mapped[str] = mapped_column(String(8))
    orders: Mapped[list[Order]] = relationship(back_populates="product")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reference: Mapped[str] = mapped_column(String(64), unique=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    amount: Mapped[str] = mapped_column(String(32))
    currency: Mapped[str] = mapped_column(String(8))
    status: Mapped[str] = mapped_column(String(32), default="pending")
    product: Mapped[Product] = relationship(back_populates="orders")


class Transfer(Base):
    __tablename__ = "transfers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reference: Mapped[str] = mapped_column(String(64), unique=True)
    amount: Mapped[str] = mapped_column(String(32))
    currency: Mapped[str] = mapped_column(String(8))
    destination: Mapped[str] = mapped_column(String(64), default="")
    status: Mapped[str] = mapped_column(String(32), default="pending")


DEMO_PRODUCTS = [
    {"sku": "DEMO-SHIRT", "name": "Demo T-shirt", "description": "Cotton demo shirt", "price": "25.00", "currency": "USD"},
    {"sku": "DEMO-COFFEE", "name": "Demo coffee", "description": "A cup of demo coffee", "price": "5.00", "currency": "USD"},
    {"sku": "DEMO-BUNDLE", "name": "Demo bundle", "description": "Shirt plus coffee", "price": "10.00", "currency": "USD"},
]


def ensure_working_db() -> None:
    if not DB_PATH.exists() and INITIAL_DB.exists():
        DB_PATH.write_bytes(INITIAL_DB.read_bytes())
    Base.metadata.create_all(engine)


def seed_products() -> int:
    ensure_working_db()
    created = 0
    with SessionLocal() as session:
        for item in DEMO_PRODUCTS:
            existing = session.query(Product).filter_by(sku=item["sku"]).first()
            if existing is None:
                session.add(Product(**item))
                created += 1
        session.commit()
    return created
