from __future__ import annotations

from datetime import datetime

from app.adapters.outbound.bankin.bankin_client import BankInClient
from app.application.repair_service import RepairService
from app.domain.errors import (
    ActiveBudgetAlreadyExistsError,
    BudgetAlreadyDecidedError,
    BudgetNotFoundError,
    RepairNotReadyForBudgetError,
    SparePartNotFoundError,
)
from app.domain.models import Budget, BudgetLineItem, BudgetStatus, RepairStatus
from app.domain.ports import BudgetRepository, SparePartRepository

BANKIN_NOTE = "Taller naveSpace - reparacion"


class BudgetService:
    def __init__(
        self,
        budgets: BudgetRepository,
        parts: SparePartRepository,
        repairs: RepairService,
        bankin_client: BankInClient,
    ):
        self._budgets = budgets
        self._parts = parts
        self._repairs = repairs
        self._bankin = bankin_client

    def get(self, budget_id: int) -> Budget:
        budget = self._budgets.get(budget_id)
        if budget is None:
            raise BudgetNotFoundError(budget_id)
        return budget

    def list_by_repair(self, repair_id: int) -> list[Budget]:
        return self._budgets.list_by_repair(repair_id)

    def create(self, repair_id: int, items: list[dict]) -> Budget:
        repair = self._repairs.get(repair_id)
        if repair.status != RepairStatus.EN_TRABAJO:
            raise RepairNotReadyForBudgetError(repair_id, repair.status.value)

        existing_pending = self._budgets.find_pending_by_repair(repair_id)
        if existing_pending is not None:
            raise ActiveBudgetAlreadyExistsError(repair_id)

        line_items: list[BudgetLineItem] = []
        total = 0.0
        for item in items:
            part = self._parts.get(item["spare_part_id"])
            if part is None:
                raise SparePartNotFoundError(item["spare_part_id"])
            quantity = item["quantity"]
            subtotal = round(part.price * quantity, 2)
            total += subtotal
            line_items.append(
                BudgetLineItem(
                    id=None,
                    spare_part_id=part.id,
                    spare_part_name=part.name,
                    unit_price=part.price,
                    quantity=quantity,
                    subtotal=subtotal,
                )
            )

        budget = Budget(
            id=None,
            repair_id=repair_id,
            status=BudgetStatus.PENDIENTE,
            line_items=line_items,
            total_amount=round(total, 2),
        )
        created = self._budgets.add(budget)
        self._repairs.move_to_awaiting_budget_approval(repair_id)
        return created

    def approve(self, budget_id: int, card_id: str) -> Budget:
        budget = self.get(budget_id)
        if budget.status != BudgetStatus.PENDIENTE:
            raise BudgetAlreadyDecidedError(budget_id, budget.status.value)

        # Puede lanzar BankInCardNotFoundError / BankInChargeRejectedError / BankInConfigError /
        # BankInUnavailableError — el presupuesto queda PENDIENTE si esto falla (no se atrapa acá).
        charge = self._bankin.charge(card_id, budget.total_amount, BANKIN_NOTE)

        budget.status = BudgetStatus.APROBADO
        budget.bankin_transaction_id = charge.transaction_id
        budget.amount_charged = charge.amount
        budget.decided_at = datetime.utcnow()
        updated = self._budgets.update(budget)
        self._repairs.move_to_en_trabajo(budget.repair_id)
        return updated

    def reject(self, budget_id: int) -> Budget:
        budget = self.get(budget_id)
        if budget.status != BudgetStatus.PENDIENTE:
            raise BudgetAlreadyDecidedError(budget_id, budget.status.value)

        budget.status = BudgetStatus.RECHAZADO
        budget.decided_at = datetime.utcnow()
        updated = self._budgets.update(budget)
        self._repairs.move_to_en_trabajo(budget.repair_id)
        return updated
