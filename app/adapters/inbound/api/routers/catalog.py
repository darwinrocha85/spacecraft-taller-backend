from fastapi import APIRouter

from app.domain.damage_catalog import DAMAGE_CATALOG

router = APIRouter(prefix="/api/catalog", tags=["catalog"])


@router.get("/damages")
def get_damage_catalog() -> dict:
    # Misma forma que exponía Java en GET /api/repairs/damage-catalog:
    # { "CATEGORIA": { "label": "...", "subtypes": [...] }, ... }
    return DAMAGE_CATALOG
