from tests.conftest import create_repair


def _advance_to_en_trabajo(client, spacecraft_id):
    repair = create_repair(client, spacecraft_id=spacecraft_id)
    repair_id = repair["id"]
    client.post(f"/api/repairs/{repair_id}/confirm-receipt")
    client.patch(f"/api/repairs/{repair_id}/status", json={"status": "EN_REVISION"})
    client.patch(f"/api/repairs/{repair_id}/status", json={"status": "EN_TRABAJO"})
    return repair_id


def test_receive_requires_lista_para_salir(client):
    repair_id = _advance_to_en_trabajo(client, 20)
    resp = client.post(f"/api/repairs/{repair_id}/receive")
    assert resp.status_code == 409


def test_receive_is_idempotent(client):
    repair_id = _advance_to_en_trabajo(client, 21)
    client.patch(f"/api/repairs/{repair_id}/status", json={"status": "LISTA_PARA_SALIR"})

    first = client.post(f"/api/repairs/{repair_id}/receive")
    assert first.status_code == 200
    assert first.json()["status"] == "ENTREGADA"

    second = client.post(f"/api/repairs/{repair_id}/receive")
    assert second.status_code == 200
    assert second.json()["status"] == "ENTREGADA"


def test_reject_then_create_second_budget(client):
    repair_id = _advance_to_en_trabajo(client, 22)

    part_id = client.post(
        "/api/parts", json={"name": "Placa de blindaje", "price": 100.0, "stockQuantity": 5}
    ).json()["id"]

    budget1 = client.post(
        f"/api/repairs/{repair_id}/budgets", json={"items": [{"sparePartId": part_id, "quantity": 1}]}
    )
    assert budget1.status_code == 201
    budget1_id = budget1.json()["id"]

    # No se puede crear un segundo mientras el primero está pendiente.
    dup = client.post(
        f"/api/repairs/{repair_id}/budgets", json={"items": [{"sparePartId": part_id, "quantity": 1}]}
    )
    assert dup.status_code == 409

    reject = client.post(f"/api/repairs/{repair_id}/budgets/{budget1_id}/reject")
    assert reject.status_code == 200
    assert reject.json()["status"] == "RECHAZADO"

    # La reparación volvió a EN_TRABAJO, así que ahora sí se puede crear un segundo presupuesto.
    budget2 = client.post(
        f"/api/repairs/{repair_id}/budgets", json={"items": [{"sparePartId": part_id, "quantity": 2}]}
    )
    assert budget2.status_code == 201
