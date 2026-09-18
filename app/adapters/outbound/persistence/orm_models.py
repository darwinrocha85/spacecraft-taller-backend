from datetime import datetime

from sqlalchemy import ForeignKey, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.adapters.outbound.persistence.db import Base


class RepairORM(Base):
    __tablename__ = "repairs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    spacecraft_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    spacecraft_name: Mapped[str] = mapped_column(String, nullable=False)
    spacecraft_model: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    # Snapshots enviados por Java, guardados como texto separado por "||" (son solo display).
    closed_museum_dates_raw: Mapped[str] = mapped_column(String, nullable=False, default="")
    closed_theater_events_raw: Mapped[str] = mapped_column(String, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    damages: Mapped[list["DamageORM"]] = relationship(
        back_populates="repair", cascade="all, delete-orphan"
    )
    budgets: Mapped[list["BudgetORM"]] = relationship(
        back_populates="repair", cascade="all, delete-orphan"
    )


class DamageORM(Base):
    __tablename__ = "damages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    repair_id: Mapped[int] = mapped_column(ForeignKey("repairs.id"), nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    subtype: Mapped[str] = mapped_column(String, nullable=False)

    repair: Mapped["RepairORM"] = relationship(back_populates="damages")


class SparePartORM(Base):
    __tablename__ = "spare_parts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    stock_quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class BudgetORM(Base):
    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    repair_id: Mapped[int] = mapped_column(ForeignKey("repairs.id"), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    bankin_transaction_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    amount_charged: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    repair: Mapped["RepairORM"] = relationship(back_populates="budgets")
    line_items: Mapped[list["BudgetLineItemORM"]] = relationship(
        back_populates="budget", cascade="all, delete-orphan"
    )


class BudgetLineItemORM(Base):
    __tablename__ = "budget_line_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    budget_id: Mapped[int] = mapped_column(ForeignKey("budgets.id"), nullable=False)
    spare_part_id: Mapped[int] = mapped_column(ForeignKey("spare_parts.id"), nullable=False)
    spare_part_name: Mapped[str] = mapped_column(String, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    subtotal: Mapped[float] = mapped_column(Float, nullable=False)

    budget: Mapped["BudgetORM"] = relationship(back_populates="line_items")
