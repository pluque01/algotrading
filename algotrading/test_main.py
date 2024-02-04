from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)


def test_get_assets():
    response = client.get("/assets")
    assert response.status_code == 200


def test_get_strategies():
    response = client.get("/strategies")
    assert response.status_code == 200
    assert response.json().get("strategies") is not None
