import os
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, List
from app.schemas import TransactionScoreRequest, RiskScoreResponse, RiskDriver
from ml.train_and_eval import train_and_evaluate, NUMERICAL_FEATURES, CATEGORICAL_FEATURES

MODEL_PATH = "ml/artifacts/razorguard_model.joblib"

class RiskEngine:
    _instance = None

    def __init__(self):
        self.model = None
        self.load_or_train_model()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_or_train_model(self):
        if os.path.exists(MODEL_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
                print(f"[RiskEngine] Loaded trained model from {MODEL_PATH}")
            except Exception as e:
                print(f"[RiskEngine] Error loading model: {e}. Retraining...")
                self.model, _ = train_and_evaluate(save_artifacts=True)
        else:
            print("[RiskEngine] Model artifact not found. Triggering automated training...")
            self.model, _ = train_and_evaluate(save_artifacts=True)

    def score_transaction(self, req: TransactionScoreRequest) -> RiskScoreResponse:
        if not req.txn_id:
            req.txn_id = f"txn_{int(datetime.now().timestamp() * 1000)}"

        # Prepare single record DataFrame
        input_dict = {
            "amount": float(req.amount),
            "order_hour": int(req.order_hour if req.order_hour is not None else 14),
            "ip_delivery_distance_km": float(req.ip_delivery_distance_km),
            "txn_velocity_1h": int(req.txn_velocity_1h),
            "txn_velocity_24h": int(req.txn_velocity_24h),
            "device_fingerprint_entropy": float(req.device_fingerprint_entropy),
            "user_account_age_days": int(req.user_account_age_days),
            "historical_dispute_count": int(req.historical_dispute_count),
            "historical_rto_rate": float(req.historical_rto_rate),
            "failed_attempts_before_success": int(req.failed_attempts_before_success),
            "is_vpn_or_proxy": 1 if req.is_vpn_or_proxy else 0,
            "card_bin_country_match": 1 if req.card_bin_country_match else 0,
            "payment_mode": str(req.payment_mode),
            "item_category": str(req.item_category),
            "delivery_speed_type": str(req.delivery_speed_type),
            "ip_country": str(req.ip_country)
        }

        df = pd.DataFrame([input_dict])
        
        # Predict probability from ML model
        ml_prob = float(self.model.predict_proba(df)[0, 1])

        # Multi-layer Defense: Combine ML with critical velocity & fraud heuristics
        heuristic_score = 0.0
        if req.is_vpn_or_proxy:
            heuristic_score += 0.30
        if req.ip_country != "IN":
            heuristic_score += 0.25
        if req.txn_velocity_1h >= 4:
            heuristic_score += 0.30
        elif req.txn_velocity_1h >= 2:
            heuristic_score += 0.10
        if req.historical_rto_rate >= 0.45 and req.payment_mode == "COD":
            heuristic_score += 0.40
        if req.device_fingerprint_entropy < 0.50:
            heuristic_score += 0.25
        if not req.card_bin_country_match:
            heuristic_score += 0.25
        if req.failed_attempts_before_success >= 2:
            heuristic_score += 0.20

        # Enforce conservative defense-in-depth risk blending
        final_prob = min(1.0, max(ml_prob, heuristic_score * 0.90 if heuristic_score > 0.4 else ml_prob))
        risk_score = round(final_prob * 100.0, 1)

        # Risk Tier and Action determination
        if risk_score < 30.0:
            risk_tier = "LOW"
            action = "ALLOW"
            action_color = "emerald"
        elif risk_score < 60.0:
            risk_tier = "MEDIUM"
            action = "STEP_UP_2FA"
            action_color = "amber"
        elif risk_score < 85.0:
            risk_tier = "HIGH"
            action = "MANUAL_REVIEW"
            action_color = "orange"
        else:
            risk_tier = "CRITICAL"
            action = "BLOCK"
            action_color = "rose"

        # Extract risk drivers (Explainability)
        risk_drivers = self._extract_risk_drivers(req, risk_score)
        narrative = self._generate_underwriting_narrative(req, risk_score, risk_tier, action)

        # Calculate unit economics
        unit_economics = {
            "transaction_amount_inr": req.amount,
            "potential_loss_prevented_inr": req.amount if action == "BLOCK" else 0.0,
            "merchant_recommendation": f"Execute action '{action}' to optimize revenue safety."
        }

        return RiskScoreResponse(
            txn_id=req.txn_id,
            risk_score=risk_score,
            risk_tier=risk_tier,
            action=action,
            action_color=action_color,
            confidence_score=round(max(final_prob, 1 - final_prob) * 100, 1),
            is_anomaly=(risk_score >= 60.0),
            top_risk_drivers=risk_drivers,
            risk_narrative=narrative,
            unit_economic_impact=unit_economics
        )

    def _extract_risk_drivers(self, req: TransactionScoreRequest, score: float) -> List[RiskDriver]:
        drivers = []

        if req.is_vpn_or_proxy:
            drivers.append(RiskDriver(
                feature="VPN/Proxy Gateway",
                impact="NEGATIVE",
                description="Transaction originated from a commercial VPN/TOR exit node."
            ))

        if req.ip_country != "IN":
            drivers.append(RiskDriver(
                feature="Geo-IP Country Mismatch",
                impact="NEGATIVE",
                description=f"IP country '{req.ip_country}' deviates from destination country (IN)."
            ))

        if req.txn_velocity_1h >= 3:
            drivers.append(RiskDriver(
                feature="High Velocity Spike",
                impact="NEGATIVE",
                description=f"{req.txn_velocity_1h} transactions initiated in past 60 mins."
            ))

        if req.historical_rto_rate > 0.35 and req.payment_mode == "COD":
            drivers.append(RiskDriver(
                feature="COD Return Abuse History",
                impact="NEGATIVE",
                description=f"Customer has a {req.historical_rto_rate*100:.0f}% historical Return-To-Origin rate on COD."
            ))

        if req.device_fingerprint_entropy < 0.50:
            drivers.append(RiskDriver(
                feature="Device Fingerprint Anomaly",
                impact="NEGATIVE",
                description="Low fingerprint consistency indicating simulated or spoofed browser environment."
            ))

        if req.historical_dispute_count >= 2:
            drivers.append(RiskDriver(
                feature="Dispute Recidivism",
                impact="NEGATIVE",
                description=f"Customer linked to {req.historical_dispute_count} prior bank chargebacks."
            ))

        if req.amount > 30000 and req.user_account_age_days < 7:
            drivers.append(RiskDriver(
                feature="High Value on New Account",
                impact="NEGATIVE",
                description="Large ticket order placed on an account less than 7 days old."
            ))

        # Positive Trust Factors
        if req.user_account_age_days > 90 and req.historical_dispute_count == 0 and req.historical_rto_rate < 0.10:
            drivers.append(RiskDriver(
                feature="Established Trust Profile",
                impact="POSITIVE",
                description=f"Verified customer account aged {req.user_account_age_days} days with spotless payment history."
            ))

        if req.payment_mode == "UPI" and not req.is_vpn_or_proxy and req.ip_country == "IN":
            drivers.append(RiskDriver(
                feature="Secure Domestic UPI",
                impact="POSITIVE",
                description="Two-factor MPIN authenticated domestic transaction."
            ))

        if not drivers:
            drivers.append(RiskDriver(
                feature="Standard Baseline Profile",
                impact="NEUTRAL",
                description="Transaction parameters fall within normal merchant behavioral limits."
            ))

        return drivers

    def _generate_underwriting_narrative(self, req: TransactionScoreRequest, score: float, tier: str, action: str) -> str:
        if tier == "LOW":
            return (
                f"Transaction {req.txn_id} scored a safe {score}/100. "
                f"The order presents standard customer telemetry with domestic {req.payment_mode} routing and low velocity. "
                "Immediate checkout approval is recommended with zero customer friction."
            )
        elif tier == "MEDIUM":
            return (
                f"Transaction {req.txn_id} evaluated at moderate risk ({score}/100). "
                f"Slight velocity or amount deviation detected ({req.payment_mode} for INR {req.amount:,.2f}). "
                "Recommended step-up verification (OTP/3DS) to confirm buyer intent."
            )
        elif tier == "HIGH":
            return (
                f"Transaction {req.txn_id} flagged with HIGH risk ({score}/100). "
                f"Multiple anomalous indicators present (IP: {req.ip_country}, 1h Velocity: {req.txn_velocity_1h}, VPN: {req.is_vpn_or_proxy}). "
                "Hold order in merchant review queue before fulfillment."
            )
        else:
            return (
                f"CRITICAL RISK DETECTED ({score}/100) for transaction {req.txn_id}. "
                f"Severe abuse signals identified across device consistency and payment channel. "
                "Automated defense rules triggered: Order blocked to prevent immediate chargeback or RTO loss."
            )

risk_engine = RiskEngine.get_instance()
