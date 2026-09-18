from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


# ---- Daños ----


class DamageIn(BaseModel):
    category: str
    subtype: str


class DamageOut(BaseModel):
    category: str
    subtype: str


# ---- Reparaciones ----


class InternalRepairCreate(BaseModel):
    spacecraft_id: int = Field(alias="spacecraftId")
    spacecraft_name: str = Field(alias="spacecraftName")
    spacecraft_model: str | None = Field(default=None, alias="spacecraftModel")
    damages: list[DamageIn]
    closed_museum_dates: list[str] = Field(default_factory=list, alias="closedMuseumDates")
    closed_theater_events: list[str] = Field(default_factory=list, alias="closedTheaterEvents")

    model_config = {"populate_by_name": True}


class RepairOut(BaseModel):
    id: int
    spacecraft_id: int = Field(serialization_alias="spacecraftId")
    spacecraft_name: str = Field(serialization_alias="spacecraftName")
    spacecraft_model: str | None = Field(serialization_alias="spacecraftModel")
    status: str
    damages: list[DamageOut]
    closed_museum_dates: list[str] = Field(serialization_alias="closedMuseumDates")
    closed_theater_events: list[str] = Field(serialization_alias="closedTheaterEvents")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")
    delivered_at: datetime | None = Field(default=None, serialization_alias="deliveredAt")

    model_config = {"populate_by_name": True}


class StatusChangeIn(BaseModel):
    status: str


# ---- Repuestos ----


class SparePartCreate(BaseModel):
    name: str
    price: float
    stock_quantity: int | None = Field(default=None, alias="stockQuantity")

    model_config = {"populate_by_name": True}


class SparePartUpdate(BaseModel):
    name: str | None = None
    price: float | None = None
    stock_quantity: int | None = Field(default=None, alias="stockQuantity")
    active: bool | None = None

    model_config = {"populate_by_name": True}


class SparePartOut(BaseModel):
    id: int
    name: str
    price: float
    stock_quantity: int | None = Field(serialization_alias="stockQuantity")
    active: bool

    model_config = {"populate_by_name": True}


# ---- Presupuestos ----


class BudgetLineItemIn(BaseModel):
    spare_part_id: int = Field(alias="sparePartId")
    quantity: int

    model_config = {"populate_by_name": True}


class BudgetCreate(BaseModel):
    items: list[BudgetLineItemIn]


class BudgetLineItemOut(BaseModel):
    id: int
    spare_part_id: int = Field(serialization_alias="sparePartId")
    spare_part_name: str = Field(serialization_alias="sparePartName")
    unit_price: float = Field(serialization_alias="unitPrice")
    quantity: int
    subtotal: float

    model_config = {"populate_by_name": True}


class BudgetOut(BaseModel):
    id: int
    repair_id: int = Field(serialization_alias="repairId")
    status: str
    line_items: list[BudgetLineItemOut] = Field(serialization_alias="lineItems")
    total_amount: float = Field(serialization_alias="totalAmount")
    bankin_transaction_id: int | None = Field(serialization_alias="bankinTransactionId")
    amount_charged: float | None = Field(serialization_alias="amountCharged")
    created_at: datetime = Field(serialization_alias="createdAt")
    decided_at: datetime | None = Field(serialization_alias="decidedAt")

    model_config = {"populate_by_name": True}


class BudgetApproveIn(BaseModel):
    card_id: str = Field(alias="cardId")

    model_config = {"populate_by_name": True}
