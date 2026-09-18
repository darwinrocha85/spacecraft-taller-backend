from __future__ import annotations

from datetime import datetime

from app.domain.damage_catalog import is_valid_damage
from app.domain.errors import (
    ActiveRepairNotFoundError,
    InvalidDamageError,
    InvalidStatusTransitionError,
    RepairNotFoundError,
    RepairNotReadyForPickupError,
)
from app.domain.models import ALLOWED_MANUAL_TRANSITIONS, Damage, Repair, RepairStatus
from app.domain.ports import RepairRepository


class RepairService:
    def __init__(self, repairs: RepairRepository):
        self._repairs = repairs

    def create_from_java(
        self,
        spacecraft_id: int,
        spacecraft_name: str,
        spacecraft_model: str | None,
        damages: list[dict],
        closed_museum_dates: list[str],
        closed_theater_events: list[str],
    ) -> tuple[Repair, bool]:
        """Crea la reparación pedida por Java al enviar una nave a taller.

        Devuelve (repair, created) — created=False si ya existía una reparación activa para esa
        nave (idempotencia: Java puede reintentar tras un timeout sin duplicar el registro).
        """
        existing = self._repairs.find_active_by_spacecraft(spacecraft_id)
        if existing is not None:
            return existing, False

        if not damages:
            raise InvalidDamageError("(ninguna)", "(ninguna)")
        for d in damages:
            if not is_valid_damage(d["category"], d["subtype"]):
                raise InvalidDamageError(d["category"], d["subtype"])

        repair = Repair(
            id=None,
            spacecraft_id=spacecraft_id,
            spacecraft_name=spacecraft_name,
            spacecraft_model=spacecraft_model,
            status=RepairStatus.ENVIADA,
            damages=[Damage(id=None, category=d["category"], subtype=d["subtype"]) for d in damages],
            closed_museum_dates=closed_museum_dates,
            closed_theater_events=closed_theater_events,
        )
        return self._repairs.add(repair), True

    def get(self, repair_id: int) -> Repair:
        repair = self._repairs.get(repair_id)
        if repair is None:
            raise RepairNotFoundError(repair_id)
        return repair

    def get_active_for_spacecraft(self, spacecraft_id: int) -> Repair:
        repair = self._repairs.find_active_by_spacecraft(spacecraft_id)
        if repair is None:
            raise ActiveRepairNotFoundError(spacecraft_id)
        return repair

    def list_by_spacecraft(self, spacecraft_id: int) -> list[Repair]:
        return self._repairs.list_by_spacecraft(spacecraft_id)

    def list_all(self, status: RepairStatus | None = None) -> list[Repair]:
        return self._repairs.list_all(status)

    def confirm_receipt(self, repair_id: int) -> Repair:
        return self._transition(repair_id, RepairStatus.RECIBIDA)

    def advance_status(self, repair_id: int, new_status: RepairStatus) -> Repair:
        return self._transition(repair_id, new_status)

    def receive(self, repair_id: int) -> Repair:
        """El dueño de la flota confirma que retiró la nave. Idempotente."""
        repair = self.get(repair_id)
        if repair.status == RepairStatus.ENTREGADA:
            return repair
        if repair.status != RepairStatus.LISTA_PARA_SALIR:
            raise RepairNotReadyForPickupError(repair_id, repair.status.value)
        repair.status = RepairStatus.ENTREGADA
        repair.delivered_at = datetime.utcnow()
        return self._repairs.update(repair)

    def move_to_awaiting_budget_approval(self, repair_id: int) -> Repair:
        repair = self.get(repair_id)
        repair.status = RepairStatus.ESPERANDO_APROBACION_PRESUPUESTO
        return self._repairs.update(repair)

    def move_to_en_trabajo(self, repair_id: int) -> Repair:
        """Efecto lateral tras aprobar o rechazar un presupuesto: vuelve a EN_TRABAJO."""
        repair = self.get(repair_id)
        repair.status = RepairStatus.EN_TRABAJO
        return self._repairs.update(repair)

    def _transition(self, repair_id: int, new_status: RepairStatus) -> Repair:
        repair = self.get(repair_id)
        allowed = ALLOWED_MANUAL_TRANSITIONS.get(repair.status, set())
        if new_status not in allowed:
            raise InvalidStatusTransitionError(repair.status.value, new_status.value)
        repair.status = new_status
        return self._repairs.update(repair)
