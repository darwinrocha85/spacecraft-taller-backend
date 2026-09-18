"""Entidades de dominio, sin dependencias de framework (ni FastAPI ni SQLAlchemy)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class RepairStatus(str, Enum):
    """Estado de una reparación dentro del taller.

    ENVIADA: creada por spacecraftSystem (Java) al mandar la nave; el taller
             todavía no confirmó que la recibió.
    RECIBIDA: el taller confirmó recepción física de la nave.
    EN_REVISION: el taller está evaluando los daños.
    EN_TRABAJO: se está reparando (o esperando que se apruebe un presupuesto
                para poder seguir).
    ESPERANDO_APROBACION_PRESUPUESTO: hay un presupuesto pendiente de que el
                dueño de la nave lo apruebe o rechace.
    LISTA_PARA_SALIR: la reparación terminó, la nave puede ser retirada.
    ENTREGADA: el dueño confirmó que retiró la nave (estado terminal).
    """

    ENVIADA = "ENVIADA"
    RECIBIDA = "RECIBIDA"
    EN_REVISION = "EN_REVISION"
    EN_TRABAJO = "EN_TRABAJO"
    ESPERANDO_APROBACION_PRESUPUESTO = "ESPERANDO_APROBACION_PRESUPUESTO"
    LISTA_PARA_SALIR = "LISTA_PARA_SALIR"
    ENTREGADA = "ENTREGADA"


TERMINAL_STATUSES = {RepairStatus.ENTREGADA}

# Transiciones manuales permitidas, ademas de las que disparan como efecto
# lateral de una accion de presupuesto (ver application/repair_service.py).
ALLOWED_MANUAL_TRANSITIONS: dict[RepairStatus, set[RepairStatus]] = {
    RepairStatus.ENVIADA: {RepairStatus.RECIBIDA},
    RepairStatus.RECIBIDA: {RepairStatus.EN_REVISION},
    RepairStatus.EN_REVISION: {RepairStatus.EN_TRABAJO},
    RepairStatus.EN_TRABAJO: {RepairStatus.LISTA_PARA_SALIR},
    RepairStatus.ESPERANDO_APROBACION_PRESUPUESTO: set(),
    RepairStatus.LISTA_PARA_SALIR: set(),
    RepairStatus.ENTREGADA: set(),
}


class BudgetStatus(str, Enum):
    PENDIENTE = "PENDIENTE"
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"


@dataclass
class Damage:
    id: int | None
    category: str
    subtype: str


@dataclass
class Repair:
    id: int | None
    spacecraft_id: int
    spacecraft_name: str
    spacecraft_model: str | None
    status: RepairStatus
    damages: list[Damage] = field(default_factory=list)
    closed_museum_dates: list[str] = field(default_factory=list)
    closed_theater_events: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    delivered_at: datetime | None = None

    def is_active(self) -> bool:
        return self.status not in TERMINAL_STATUSES


@dataclass
class SparePart:
    id: int | None
    name: str
    price: float
    stock_quantity: int | None = None
    active: bool = True


@dataclass
class BudgetLineItem:
    id: int | None
    spare_part_id: int
    spare_part_name: str
    unit_price: float
    quantity: int
    subtotal: float


@dataclass
class Budget:
    id: int | None
    repair_id: int
    status: BudgetStatus
    line_items: list[BudgetLineItem] = field(default_factory=list)
    total_amount: float = 0.0
    bankin_transaction_id: int | None = None
    amount_charged: float | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    decided_at: datetime | None = None
