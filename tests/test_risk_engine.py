import pytest
from app.schemas import TransactionScoreRequest
from app.services.risk_engine import risk_engine

def test_legitimate_upi_transaction():
    req = TransactionScoreRequest(
        txn_id="test_safe_001",
        amount=1200.0,
        payment_mode="UPI",
        item_category="GROCERY",
        ip_country="IN",
        ip_delivery_distance_km=5.0,
        is_vpn_or_proxy=False,
        txn_velocity_1h=1,
        txn_velocity_24h=1,
        user_account_age_days=300,
        historical_dispute_count=0,
        historical_rto_rate=0.01,
        card_bin_country_match=True,
        device_fingerprint_entropy=0.92
    )
    res = risk_engine.score_transaction(req)
    assert res.risk_tier == "LOW"
    assert res.action == "ALLOW"
    assert res.risk_score < 30.0
    assert len(res.top_risk_drivers) > 0

def test_stolen_card_high_risk_transaction():
    req = TransactionScoreRequest(
        txn_id="test_fraud_001",
        amount=75000.0,
        payment_mode="CREDIT_CARD",
        item_category="ELECTRONICS",
        ip_country="US",
        ip_delivery_distance_km=2500.0,
        is_vpn_or_proxy=True,
        txn_velocity_1h=7,
        txn_velocity_24h=12,
        user_account_age_days=2,
        historical_dispute_count=1,
        historical_rto_rate=0.15,
        card_bin_country_match=False,
        device_fingerprint_entropy=0.25,
        failed_attempts_before_success=2
    )
    res = risk_engine.score_transaction(req)
    assert res.risk_tier in ["HIGH", "CRITICAL"]
    assert res.action in ["MANUAL_REVIEW", "BLOCK"]
    assert res.risk_score >= 60.0
    assert any(d.impact == "NEGATIVE" for d in res.top_risk_drivers)
