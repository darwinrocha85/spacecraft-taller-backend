import uuid

import pytest


@pytest.fixture()
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("AUTO_SEED", "false")
    monkeypatch.setenv("TALLER_INTERNAL_API_KEY", "test-internal-key")
    monkeypatch.setenv("BANKIN_API_BASE", "http://bankin.invalid")
    monkeypatch.setenv("BANKIN_API_KEY", "")

    from app.adapters.outbound.persistence import db
    from app.main import app

    db_path = tmp_path / f"test_{uuid.uuid4().hex}.db"
    db.configure(str(db_path))

    from fastapi.testclient import TestClient

    with TestClient(app) as test_client:
        yield test_client


INTERNAL_HEADERS = {"X-Internal-Api-Key": "test-internal-key"}


def create_repair(client, spacecraft_id=1, damages=None):
    damages = damages or [{"category": "PROPULSION", "subtype": "Motor principal"}]
    resp = client.post(
        "/api/internal/repairs",
        json={
            "spacecraftId": spacecraft_id,
            "spacecraftName": "USS Test",
            "spacecraftModel": "Test-class",
            "damages": damages,
            "closedMuseumDates": [],
            "closedTheaterEvents": [],
        },
        headers=INTERNAL_HEADERS,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()
