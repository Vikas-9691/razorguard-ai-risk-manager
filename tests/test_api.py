import pytest
from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_overview_stats():
    res = client.get("/api/v1/overview-stats")
    assert res.status_code == 200
    data = res.json()
    assert "total_scanned_transactions" in data
    assert "prevented_loss_inr" in data

def test_api_benchmark_metrics():
    res = client.get("/api/v1/benchmark/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "held_out_metrics" in data
    assert "precision" in data["held_out_metrics"]
    assert "recall" in data["held_out_metrics"]
    assert "unit_economics" in data

def test_api_score_transaction():
    payload = {
        "amount": 3200.0,
        "payment_mode": "UPI",
        "item_category": "APPAREL",
        "txn_velocity_1h": 1,
        "txn_velocity_24h": 1,
        "user_account_age_days": 150,
        "historical_rto_rate": 0.05,
        "ip_country": "IN",
        "ip_delivery_distance_km": 15.0,
        "is_vpn_or_proxy": False,
        "card_bin_country_match": True,
        "device_fingerprint_entropy": 0.90,
        "historical_dispute_count": 0,
        "failed_attempts_before_success": 0
    }
    res = client.post("/api/v1/risk/score", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "risk_score" in data
    assert "risk_tier" in data
    assert "action" in data
    assert "top_risk_drivers" in data

def test_api_abuse_rings():
    res = client.get("/api/v1/abuse-rings")
    assert res.status_code == 200
    data = res.json()
    assert "clusters" in data
    assert "network_graph" in data
    assert len(data["clusters"]) > 0

def test_api_disputes():
    res = client.get("/api/v1/disputes")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
