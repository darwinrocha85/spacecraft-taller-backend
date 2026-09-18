from unittest.mock import patch

import httpx

from app.adapters.outbound.bankin.bankin_client import ChargeResult
from app.domain.errors import (
    BankInCardNotFoundError,
    BankInChargeRejectedError,
    BankInConfigError,
    BankInUnavailableError,
)
from tests.conftest import create_repair


def _setup_budget(client, spacecraft_id):
    repair = create_repair(client, spacecraft_id=spacecraft_id)
    repair_id = repair["id"]
    client.post(f"/api/repairs/{repair_id}/confirm-receipt")
    client.patch(f"/api/repairs/{repair_id}/status", json={"status": "EN_REVISION"})
    client.patch(f"/api/repairs/{repair_id}/status", json={"status": "EN_TRABAJO"})

    part_id = client.post(
        "/api/parts", json={"name": "Placa de blindaje", "price": 180.0, "stockQuantity": 5}
    ).json()["id"]
    budget = client.post(
        f"/api/repairs/{repair_id}/budgets", json={"items": [{"sparePartId": part_id, "quantity": 1}]}
    ).json()
    return repair_id, budget["id"]


def test_approve_budget_happy_path(client):
    repair_id, budget_id = _setup_budget(client, 30)

    with patch(
        "app.adapters.outbound.bankin.bankin_client.BankInClient.charge",
        return_value=ChargeResult(transaction_id=999, amount=180.0),
    ):
        resp = client.post(
            f"/api/repairs/{repair_id}/budgets/{budget_id}/approve", json={"cardId": "card-1"}
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "APROBADO"
    assert body["bankinTransactionId"] == 999

    repair = client.get(f"/api/repairs/{repair_id}").json()
    assert repair["status"] == "EN_TRABAJO"


def test_approve_budget_card_not_found(client):
    repair_id, budget_id = _setup_budget(client, 31)
    with patch(
        "app.adapters.outbound.bankin.bankin_client.BankInClient.charge",
        side_effect=BankInCardNotFoundError("Tarjeta no encontrada"),
    ):
        resp = client.post(
            f"/api/repairs/{repair_id}/budgets/{budget_id}/approve", json={"cardId": "bad-card"}
        )
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Tarjeta no encontrada"

    budget = client.get(f"/api/repairs/{repair_id}/budgets").json()[0]
    assert budget["status"] == "PENDIENTE"


def test_approve_budget_charge_rejected(client):
    repair_id, budget_id = _setup_budget(client, 32)
    with patch(
        "app.adapters.outbound.bankin.bankin_client.BankInClient.charge",
        side_effect=BankInChargeRejectedError("Fondos insuficientes"),
    ):
        resp = client.post(
            f"/api/repairs/{repair_id}/budgets/{budget_id}/approve", json={"cardId": "card-1"}
        )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Fondos insuficientes"


def test_approve_budget_config_error_hides_detail(client):
    repair_id, budget_id = _setup_budget(client, 33)
    with patch(
        "app.adapters.outbound.bankin.bankin_client.BankInClient.charge",
        side_effect=BankInConfigError(),
    ):
        resp = client.post(
            f"/api/repairs/{repair_id}/budgets/{budget_id}/approve", json={"cardId": "card-1"}
        )
    assert resp.status_code == 500
    assert resp.json()["detail"] == "Ocurrió un error inesperado. Intenta de nuevo más tarde."


def test_approve_budget_bankin_unavailable(client):
    repair_id, budget_id = _setup_budget(client, 34)
    with patch(
        "app.adapters.outbound.bankin.bankin_client.BankInClient.charge",
        side_effect=BankInUnavailableError(),
    ):
        resp = client.post(
            f"/api/repairs/{repair_id}/budgets/{budget_id}/approve", json={"cardId": "card-1"}
        )
    assert resp.status_code == 502
    assert "BankIn" in resp.json()["detail"]


def test_bankin_client_real_http_error_mapping(monkeypatch):
    """Sin mockear el método, verifica que BankInClient.charge() mapea bien un 404 real de httpx."""
    from app.adapters.outbound.bankin.bankin_client import BankInClient

    class FakeResponse:
        status_code = 404

        def json(self):
            return {"detail": "Tarjeta no encontrada en BankIn"}

    def fake_post(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(httpx, "post", fake_post)
    client_obj = BankInClient(api_base="http://bankin.invalid", api_key="")
    try:
        client_obj.charge("card-x", 10.0, "note")
        assert False, "debía lanzar BankInCardNotFoundError"
    except BankInCardNotFoundError as exc:
        assert exc.detail == "Tarjeta no encontrada en BankIn"
