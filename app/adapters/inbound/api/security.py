import os

from fastapi import Header, HTTPException


def require_internal_key(x_internal_api_key: str | None = Header(default=None)) -> None:
    """A diferencia del resto del demo (sin auth), el canal Java -> taller SIEMPRE exige clave,
    incluso si TALLER_INTERNAL_API_KEY no está configurada (fail-closed, es el único punto de
    confianza servidor-a-servidor de todo el sistema)."""
    expected = os.environ.get("TALLER_INTERNAL_API_KEY", "")
    if not expected or x_internal_api_key != expected:
        raise HTTPException(status_code=401, detail="Clave interna inválida o ausente")
