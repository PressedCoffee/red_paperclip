import pytest
from fastapi.testclient import TestClient
from backend_api.api import app, API_TOKEN, API_ENABLED

client = TestClient(app)

AUTH_HEADER = {"Authorization": API_TOKEN}
INVALID_AUTH_HEADER = {"Authorization": "invalid-token"}


def test_agents_endpoint_auth():
    # Without auth
    response = client.get("/agents/")
    assert response.status_code == 403

    # With invalid auth
    response = client.get("/agents/", headers=INVALID_AUTH_HEADER)
    assert response.status_code == 403

    # With valid auth
    response = client.get("/agents/", headers=AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert "agent_id" in data[0]
    assert "correlation_id" in data[0]
    assert "timestamp" in data[0]


def test_trades_endpoint():
    response = client.get("/trades/", headers=AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert "trade_id" in data[0]


def test_coalitions_endpoint():
    response = client.get("/coalitions/", headers=AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert "coalition_id" in data[0]


def test_payments_endpoint():
    response = client.get("/payments/", headers=AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert "payment_id" in data[0]


def test_capsules_endpoint():
    response = client.get("/capsules/", headers=AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert "capsule_id" in data[0]


def test_api_disabled(monkeypatch):
    # Temporarily disable API feature flag
    monkeypatch.setattr("backend_api.api.API_ENABLED", False)
    response = client.get("/agents/", headers=AUTH_HEADER)
    assert response.status_code == 403
    assert response.json()["detail"] == "API is disabled by feature flag"
