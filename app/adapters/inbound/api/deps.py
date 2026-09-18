from fastapi import Depends
from sqlalchemy.orm import Session

from app.adapters.outbound.bankin.bankin_client import BankInClient
from app.adapters.outbound.persistence.budget_repository_sqlite import SqliteBudgetRepository
from app.adapters.outbound.persistence.db import get_session
from app.adapters.outbound.persistence.repair_repository_sqlite import SqliteRepairRepository
from app.adapters.outbound.persistence.spare_part_repository_sqlite import (
    SqliteSparePartRepository,
)
from app.application.budget_service import BudgetService
from app.application.parts_service import PartsService
from app.application.repair_service import RepairService


def get_repair_service(session: Session = Depends(get_session)) -> RepairService:
    return RepairService(SqliteRepairRepository(session))


def get_parts_service(session: Session = Depends(get_session)) -> PartsService:
    return PartsService(SqliteSparePartRepository(session))


def get_bankin_client() -> BankInClient:
    return BankInClient()


def get_budget_service(
    session: Session = Depends(get_session),
    bankin_client: BankInClient = Depends(get_bankin_client),
) -> BudgetService:
    return BudgetService(
        SqliteBudgetRepository(session),
        SqliteSparePartRepository(session),
        RepairService(SqliteRepairRepository(session)),
        bankin_client,
    )
