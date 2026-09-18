from fastapi import APIRouter, Depends, HTTPException

from app.adapters.inbound.api.deps import get_budget_service, get_repair_service
from app.adapters.inbound.api.schemas import BudgetApproveIn, BudgetOut, RepairOut
from app.application.budget_service import BudgetService
from app.application.repair_service import RepairService
from app.domain.errors import (
    BankInCardNotFoundError,
    BankInChargeRejectedError,
    BankInConfigError,
    BankInUnavailableError,
    BudgetAlreadyDecidedError,
    BudgetNotFoundError,
    RepairNotFoundError,
    RepairNotReadyForPickupError,
)

router = APIRouter(prefix="/api/repairs", tags=["owner"])

GENERIC_ERROR_MESSAGE = "Ocurrió un error inesperado. Intenta de nuevo más tarde."


@router.post("/{repair_id}/budgets/{budget_id}/approve", response_model=BudgetOut)
def approve_budget(
    repair_id: int,
    budget_id: int,
    payload: BudgetApproveIn,
    service: BudgetService = Depends(get_budget_service),
):
    try:
        return service.approve(budget_id, payload.card_id)
    except BudgetNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except BudgetAlreadyDecidedError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except BankInCardNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail) from exc
    except BankInChargeRejectedError as exc:
        raise HTTPException(status_code=400, detail=exc.detail) from exc
    except BankInConfigError as exc:
        raise HTTPException(status_code=500, detail=GENERIC_ERROR_MESSAGE) from exc
    except BankInUnavailableError as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "No se pudo conectar con BankIn. Asegurate de que la app de BankIn este "
                "corriendo (y que BANKIN_API_BASE apunte a esa URL) e intenta de nuevo."
            ),
        ) from exc


@router.post("/{repair_id}/budgets/{budget_id}/reject", response_model=BudgetOut)
def reject_budget(
    repair_id: int, budget_id: int, service: BudgetService = Depends(get_budget_service)
):
    try:
        return service.reject(budget_id)
    except BudgetNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except BudgetAlreadyDecidedError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{repair_id}/receive", response_model=RepairOut)
def receive_ship(repair_id: int, service: RepairService = Depends(get_repair_service)):
    try:
        return service.receive(repair_id)
    except RepairNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RepairNotReadyForPickupError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
