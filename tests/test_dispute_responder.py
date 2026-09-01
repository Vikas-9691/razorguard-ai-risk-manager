import pytest
from app.schemas import DisputeCreateRequest
from app.services.dispute_responder import dispute_responder

def test_dispute_dossier_generation():
    req = DisputeCreateRequest(
        dispute_id="DSP_TEST_99",
        txn_id="txn_test_7788",
        amount=19500.0,
        dispute_reason="10.4: Other Fraud - Card-Absent Environment",
        bank_arn="ARN-99887766554433",
        customer_name="Vikram Sethi",
        customer_email="vikram.sethi@example.com",
        courier_name="BlueDart Express",
        tracking_awb="BLUEDART-IND-884920",
        delivery_timestamp="2026-08-20T15:30:00",
        otp_authenticated=True,
        three_ds_auth_success=True
    )
    res = dispute_responder.generate_defense_package(req)
    assert res.dispute_id == "DSP_TEST_99"
    assert res.status == "AUTO_DEFENDED"
    assert res.win_probability_pct >= 90.0
    assert "FORMAL CHARGEBACK REBUTTAL DOSSIER" in res.markdown_defense_letter
    assert "10.4" in res.markdown_defense_letter
    assert "Liability Shift" in res.markdown_defense_letter
