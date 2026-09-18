from tests.conftest import create_repair


def test_full_shop_transition_flow(client):
    repair = create_repair(client, spacecraft_id=10)
    repair_id = repair["id"]

    resp = client.post(f"/api/repairs/{repair_id}/confirm-receipt")
    assert resp.status_code == 200
    assert resp.json()["status"] == "RECIBIDA"

    resp = client.patch(f"/api/repairs/{repair_id}/status", json={"status": "EN_REVISION"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "EN_REVISION"

    resp = client.patch(f"/api/repairs/{repair_id}/status", json={"status": "EN_TRABAJO"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "EN_TRABAJO"


def test_confirm_receipt_twice_is_rejected(client):
    repair = create_repair(client, spacecraft_id=11)
    repair_id = repair["id"]
    client.post(f"/api/repairs/{repair_id}/confirm-receipt")

    resp = client.post(f"/api/repairs/{repair_id}/confirm-receipt")
    assert resp.status_code == 409


def test_status_endpoint_rejects_skipping_steps(client):
    repair = create_repair(client, spacecraft_id=12)
    repair_id = repair["id"]
    # Todavía está en ENVIADA, no puede saltar directo a EN_TRABAJO.
    resp = client.patch(f"/api/repairs/{repair_id}/status", json={"status": "EN_TRABAJO"})
    assert resp.status_code == 409


def test_status_endpoint_rejects_recibida_as_target(client):
    """RECIBIDA solo se alcanza por confirm-receipt, no por el PATCH genérico."""
    repair = create_repair(client, spacecraft_id=13)
    repair_id = repair["id"]
    resp = client.patch(f"/api/repairs/{repair_id}/status", json={"status": "RECIBIDA"})
    assert resp.status_code == 409
