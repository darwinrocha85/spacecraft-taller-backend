from fastapi import APIRouter, Depends, HTTPException

from app.adapters.inbound.api.deps import get_budget_service, get_repair_service
from app.adapters.inbound.api.schemas import BudgetCreate, BudgetOut, RepairOut, StatusChangeIn
from app.application.budget_service import BudgetService
from app.application.repair_service import RepairService
from app.domain.errors import (
    ActiveBudgetAlreadyExistsError,
    InvalidStatusTransitionError,
    RepairNotFoundError,
    RepairNotReadyForBudgetError,
    SparePartNotFoundError,
)
from app.domain.models import RepairStatus

router = APIRouter(prefix="/api/repairs", tags=["shop"])

# El PATCH /status genérico solo sirve para estas transiciones manuales del taller;
# ENVIADA -> RECIBIDA tiene su propio endpoint semántico (confirm-receipt) más abajo.
_STATUS_ENDPOINT_ALLOWED_TARGETS = {
    RepairStatus.EN_REVISION,
    RepairStatus.EN_TRABAJO,
    RepairStatus.LISTA_PARA_SALIR,
}


@router.post("/{repair_id}/confirm-receipt", response_model=RepairOut)
def confirm_receipt(repair_id: int, service: RepairService = Depends(get_repair_service)):
    try:
        return service.confirm_receipt(repair_id)
    except RepairNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InvalidStatusTransitionError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.patch("/{repair_id}/status", response_model=RepairOut)
def change_status(
    repair_id: int, payload: StatusChangeIn, service: RepairService = Depends(get_repair_service)
):
    try:
        new_status = RepairStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Estado desconocido: {payload.status}") from exc

    if new_status not in _STATUS_ENDPOINT_ALLOWED_TARGETS:
        raise HTTPException(
            status_code=409,
            detail=(
                f"No se puede pasar a {new_status.value} desde este endpoint "
                "(usa confirm-receipt, o el flujo de presupuesto, según corresponda)"
            ),
        )

    try:
        return service.advance_status(repair_id, new_status)
    except RepairNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InvalidStatusTransitionError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{repair_id}/budgets", response_model=BudgetOut, status_code=201)
def create_budget(
    repair_id: int, payload: BudgetCreate, service: BudgetService = Depends(get_budget_service)
):
    try:
        items = [{"spare_part_id": i.spare_part_id, "quantity": i.quantity} for i in payload.items]
        return service.create(repair_id, items)
    except RepairNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except SparePartNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (RepairNotReadyForBudgetError, ActiveBudgetAlreadyExistsError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
