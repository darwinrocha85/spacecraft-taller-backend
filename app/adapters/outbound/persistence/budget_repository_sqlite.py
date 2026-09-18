from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.adapters.outbound.persistence.orm_models import BudgetLineItemORM, BudgetORM
from app.domain.models import Budget, BudgetLineItem, BudgetStatus
from app.domain.ports import BudgetRepository


class SqliteBudgetRepository(BudgetRepository):
    def __init__(self, session: Session):
        self._session = session

    def add(self, budget: Budget) -> Budget:
        orm = BudgetORM(
            repair_id=budget.repair_id,
            status=budget.status.value,
            total_amount=budget.total_amount,
            bankin_transaction_id=budget.bankin_transaction_id,
            amount_charged=budget.amount_charged,
        )
        orm.line_items = [
            BudgetLineItemORM(
                spare_part_id=li.spare_part_id,
                spare_part_name=li.spare_part_name,
                unit_price=li.unit_price,
                quantity=li.quantity,
                subtotal=li.subtotal,
            )
            for li in budget.line_items
        ]
        self._session.add(orm)
        self._session.commit()
        self._session.refresh(orm)
        return self._to_domain(orm)

    def get(self, budget_id: int) -> Budget | None:
        orm = self._session.get(
            BudgetORM, budget_id, options=[joinedload(BudgetORM.line_items)]
        )
        return self._to_domain(orm) if orm else None

    def list_by_repair(self, repair_id: int) -> list[Budget]:
        stmt = (
            select(BudgetORM)
            .options(joinedload(BudgetORM.line_items))
            .where(BudgetORM.repair_id == repair_id)
            .order_by(BudgetORM.created_at.desc())
        )
        rows = self._session.execute(stmt).unique().scalars().all()
        return [self._to_domain(r) for r in rows]

    def find_pending_by_repair(self, repair_id: int) -> Budget | None:
        stmt = (
            select(BudgetORM)
            .options(joinedload(BudgetORM.line_items))
            .where(BudgetORM.repair_id == repair_id)
            .where(BudgetORM.status == BudgetStatus.PENDIENTE.value)
        )
        row = self._session.execute(stmt).unique().scalars().first()
        return self._to_domain(row) if row else None

    def update(self, budget: Budget) -> Budget:
        orm = self._session.get(BudgetORM, budget.id)
        if orm is None:
            raise ValueError(f"Budget {budget.id} not found for update")
        orm.status = budget.status.value
        orm.bankin_transaction_id = budget.bankin_transaction_id
        orm.amount_charged = budget.amount_charged
        orm.decided_at = budget.decided_at
        self._session.commit()
        self._session.refresh(orm)
        return self._to_domain(orm)

    def _to_domain(self, orm: BudgetORM) -> Budget:
        return Budget(
            id=orm.id,
            repair_id=orm.repair_id,
            status=BudgetStatus(orm.status),
            line_items=[
                BudgetLineItem(
                    id=li.id,
                    spare_part_id=li.spare_part_id,
                    spare_part_name=li.spare_part_name,
                    unit_price=li.unit_price,
                    quantity=li.quantity,
                    subtotal=li.subtotal,
                )
                for li in orm.line_items
            ],
            total_amount=orm.total_amount,
            bankin_transaction_id=orm.bankin_transaction_id,
            amount_charged=orm.amount_charged,
            created_at=orm.created_at,
            decided_at=orm.decided_at,
        )
