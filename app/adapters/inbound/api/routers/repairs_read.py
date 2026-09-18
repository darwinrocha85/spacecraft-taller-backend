from fastapi import APIRouter, Depends, HTTPException, Query

from app.adapters.inbound.api.deps import get_budget_service, get_repair_service
from app.adapters.inbound.api.schemas import BudgetOut, RepairOut
from app.application.budget_service import BudgetService
from app.application.repair_service import RepairService
from app.domain.errors import ActiveRepairNotFoundError, RepairNotFoundError
from app.domain.models import RepairStatus

router = APIRouter(prefix="/api/repairs", tags=["repairs"])


@router.get("", response_model=list[RepairOut])
def list_repairs(
    spacecraft_id: int | None = Query(default=None, alias="spacecraftId"),
    status: str | None = Query(default=None),
    service: RepairService = Depends(get_repair_service),
):
    status_enum = RepairStatus(status) if status else None
    if spacecraft_id is not None:
        repairs = service.list_by_spacecraft(spacecraft_id)
        if status_enum is not None:
            repairs = [r for r in repairs if r.status == status_enum]
        return repairs
    return service.list_all(status_enum)


@router.get("/active", response_model=RepairOut)
def get_active_repair(
    spacecraft_id: int = Query(alias="spacecraftId"),
    service: RepairService = Depends(get_repair_service),
):
    try:
        return service.get_active_for_spacecraft(spacecraft_id)
    except ActiveRepairNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{repair_id}", response_model=RepairOut)
def get_repair(repair_id: int, service: RepairService = Depends(get_repair_service)):
    try:
        return service.get(repair_id)
    except RepairNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{repair_id}/budgets", response_model=list[BudgetOut])
def list_budgets(repair_id: int, service: BudgetService = Depends(get_budget_service)):
    return service.list_by_repair(repair_id)
