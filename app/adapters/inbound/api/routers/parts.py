from fastapi import APIRouter, Depends, HTTPException, Query

from app.adapters.inbound.api.deps import get_parts_service
from app.adapters.inbound.api.schemas import SparePartCreate, SparePartOut, SparePartUpdate
from app.application.parts_service import PartsService
from app.domain.errors import SparePartNotFoundError

router = APIRouter(prefix="/api/parts", tags=["parts"])


@router.get("", response_model=list[SparePartOut])
def list_parts(
    active: bool | None = Query(default=None),
    service: PartsService = Depends(get_parts_service),
):
    return service.list(active_only=bool(active))


@router.post("", response_model=SparePartOut, status_code=201)
def create_part(payload: SparePartCreate, service: PartsService = Depends(get_parts_service)):
    return service.create(payload.name, payload.price, payload.stock_quantity)


@router.patch("/{part_id}", response_model=SparePartOut)
def update_part(
    part_id: int, payload: SparePartUpdate, service: PartsService = Depends(get_parts_service)
):
    try:
        return service.update(
            part_id,
            name=payload.name,
            price=payload.price,
            stock_quantity=payload.stock_quantity,
            active=payload.active,
            stock_quantity_provided="stockQuantity" in payload.model_fields_set
            or "stock_quantity" in payload.model_fields_set,
        )
    except SparePartNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{part_id}", response_model=SparePartOut)
def deactivate_part(part_id: int, service: PartsService = Depends(get_parts_service)):
    try:
        return service.deactivate(part_id)
    except SparePartNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
