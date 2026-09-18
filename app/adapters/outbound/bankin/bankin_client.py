"""Cliente hacia BankIn, espejo de BankInPaymentService.java (mismo backend de pagos que ya usa
spacecraftSystem para las entradas). Traduce las respuestas de BankIn a las excepciones de
dominio definidas en app/domain/errors.py; los routers las convierten a HTTPException."""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass

import httpx

from app.domain.errors import (
    BankInCardNotFoundError,
    BankInChargeRejectedError,
    BankInConfigError,
    BankInUnavailableError,
)

logger = logging.getLogger("taller.bankin")

BANKIN_UNREACHABLE_MESSAGE = (
    "No se pudo conectar con BankIn. Asegurate de que la app de BankIn este corriendo "
    "(y que BANKIN_API_BASE apunte a esa URL) e intenta de nuevo."
)


@dataclass
class ChargeResult:
    transaction_id: int
    amount: float


class BankInClient:
    def __init__(self, api_base: str | None = None, api_key: str | None = None):
        self._api_base = (api_base or os.environ.get("BANKIN_API_BASE", "http://localhost:8000")).rstrip("/")
        self._api_key = api_key if api_key is not None else os.environ.get("BANKIN_API_KEY", "")

    def charge(self, card_id: str, amount: float, note: str) -> ChargeResult:
        headers = {}
        if self._api_key:
            headers["X-Api-Key"] = self._api_key

        rounded_amount = round(amount, 2)
        payload = {"card_id": card_id, "amount": rounded_amount, "note": note}

        try:
            response = httpx.post(
                f"{self._api_base}/transactions/purchase",
                json=payload,
                headers=headers,
                timeout=10.0,
            )
        except httpx.RequestError as exc:
            logger.error("No se pudo conectar con BankIn en %s: %s", self._api_base, exc)
            raise BankInUnavailableError() from exc

        if response.status_code == 201:
            body = response.json()
            return ChargeResult(transaction_id=body["id"], amount=body["amount"])

        detail = self._extract_detail(response)

        if response.status_code == 404:
            raise BankInCardNotFoundError(
                detail or "No encontramos esa tarjeta en BankIn. Verifica el numero e intenta de nuevo."
            )
        if response.status_code == 400:
            raise BankInChargeRejectedError(
                detail or "BankIn rechazo el cobro (tarjeta inactiva, saldo insuficiente o monto invalido)."
            )
        if response.status_code == 401:
            logger.error(
                "BankIn rechazo la X-Api-Key configurada (401). Revisa BANKIN_API_KEY. Respuesta: %s",
                response.text,
            )
            raise BankInConfigError()

        logger.error(
            "BankIn respondio %s en vez de 201 al cobrar la tarjeta %s", response.status_code, card_id
        )
        raise BankInConfigError()

    @staticmethod
    def _extract_detail(response: httpx.Response) -> str | None:
        try:
            body = response.json()
        except ValueError:
            return None
        detail = body.get("detail") if isinstance(body, dict) else None
        return detail if isinstance(detail, str) else None
