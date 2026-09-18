from fastapi import APIRouter, Depends, HTTPException, Response

from app.adapters.inbound.api.deps import get_repair_service
from app.adapters.inbound.api.schemas import InternalRepairCreate, RepairOut
from app.adapters.inbound.api.security import require_internal_key
from app.application.repair_service import RepairService
from app.domain.errors import InvalidDamageError

router = APIRouter(
    prefix="/api/internal",
    tags=["internal"],
    dependencies=[Depends(require_internal_key)],
)


@router.post("/repairs", response_model=RepairOut)
def create_repair(
    payload: InternalRepairCreate,
    response: Response,
    service: RepairService = Depends(get_repair_service),
):
    try:
        repair, created = service.create_from_java(
            spacecraft_id=payload.spacecraft_id,
            spacecraft_name=payload.spacecraft_name,
            spacecraft_model=payload.spacecraft_model,
            damages=[d.model_dump() for d in payload.damages],
            closed_museum_dates=payload.closed_museum_dates,
            closed_theater_events=payload.closed_theater_events,
        )
    except InvalidDamageError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    response.status_code = 201 if created else 200
    return repair
