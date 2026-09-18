from tests.conftest import INTERNAL_HEADERS, create_repair


def test_create_repair_requires_internal_key(client):
    resp = client.post(
        "/api/internal/repairs",
        json={
            "spacecraftId": 1,
            "spacecraftName": "USS Test",
            "damages": [{"category": "PROPULSION", "subtype": "Motor principal"}],
        },
    )
    assert resp.status_code == 401


def test_create_repair_happy_path(client):
    repair = create_repair(client)
    assert repair["status"] == "ENVIADA"
    assert repair["spacecraftId"] == 1
    assert repair["damages"][0]["category"] == "PROPULSION"


def test_create_repair_rejects_invalid_damage(client):
    resp = client.post(
        "/api/internal/repairs",
        json={
            "spacecraftId": 2,
            "spacecraftName": "USS Test",
            "damages": [{"category": "PROPULSION", "subtype": "No existe"}],
        },
        headers=INTERNAL_HEADERS,
    )
    assert resp.status_code == 400


def test_create_repair_is_idempotent_for_active_repair(client):
    first = create_repair(client, spacecraft_id=3)
    resp = client.post(
        "/api/internal/repairs",
        json={
            "spacecraftId": 3,
            "spacecraftName": "USS Test",
            "damages": [{"category": "COMUNICACIONES", "subtype": "Antena/transmisor"}],
        },
        headers=INTERNAL_HEADERS,
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == first["id"]
    # No duplico el daño de la segunda llamada, devolvió la reparación existente tal cual.
    assert resp.json()["damages"][0]["category"] == "PROPULSION"
