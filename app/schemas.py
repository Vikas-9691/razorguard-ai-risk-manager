from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class TransactionScoreRequest(BaseModel):
    txn_id: Optional[str] = Field(default=None, description="Transaction Reference ID")
    customer_id: str = Field(default="cust_101", description="Customer ID")
    device_id: str = Field(default="dev_990", description="Device Fingerprint ID")
    amount: float = Field(..., gt=0, description="Amount in INR")
    payment_mode: str = Field(default="UPI", description="UPI, CREDIT_CARD, DEBIT_CARD, NETBANKING, COD, WALLET, BNPL")
    item_category: str = Field(default="ELECTRONICS", description="ELECTRONICS, JEWELLERY, APPAREL, GAMING_VOUCHER, GROCERY, TRAVEL_TICKET")
    delivery_speed_type: str = Field(default="STANDARD", description="STANDARD, EXPRESS, SAME_DAY")
    delivery_city: str = Field(default="Bengaluru", description="Delivery City")
    pincode: str = Field(default="560001", description="Delivery PIN code")
    ip_country: str = Field(default="IN", description="ISO Country Code of IP")
    ip_delivery_distance_km: float = Field(default=15.0, description="Distance between IP Geo and delivery pin in km")
    is_vpn_or_proxy: bool = Field(default=False, description="Whether connection is VPN/TOR/Proxy")
    txn_velocity_1h: int = Field(default=1, ge=0, description="Transactions initiated in last 1 hour")
    txn_velocity_24h: int = Field(default=1, ge=0, description="Transactions initiated in last 24 hours")
    device_fingerprint_entropy: float = Field(default=0.88, ge=0.0, le=1.0, description="Device fingerprint consistency")
    user_account_age_days: int = Field(default=180, ge=0, description="Account age in days")
    historical_dispute_count: int = Field(default=0, ge=0, description="Number of past chargebacks")
    historical_rto_rate: float = Field(default=0.05, ge=0.0, le=1.0, description="Past Return-to-Origin rate")
    card_bin_country_match: bool = Field(default=True, description="Card issuing country matches IP country")
    failed_attempts_before_success: int = Field(default=0, ge=0, description="Prior failed CVV/OTP attempts")
    order_hour: Optional[int] = Field(default=14, ge=0, le=23, description="Hour of day (0-23)")

class RiskDriver(BaseModel):
    feature: str
    impact: str  # POSITIVE, NEGATIVE, NEUTRAL
    description: str

class RiskScoreResponse(BaseModel):
    txn_id: str
    risk_score: float  # 0 to 100
    risk_tier: str  # LOW, MEDIUM, HIGH, CRITICAL
    action: str  # ALLOW, STEP_UP_2FA, MANUAL_REVIEW, BLOCK
    action_color: str
    confidence_score: float
    is_anomaly: bool
    top_risk_drivers: List[RiskDriver]
    risk_narrative: str
    unit_economic_impact: Dict[str, Any]

class DisputeCreateRequest(BaseModel):
    dispute_id: Optional[str] = None
    txn_id: str
    amount: float
    dispute_reason: str = "10.4: Other Fraud - Card-Absent Environment"
    bank_arn: Optional[str] = "ARN-74920482019482"
    customer_name: str = "Rajesh Verma"
    customer_email: str = "rajesh.v@example.com"
    courier_name: str = "BlueDart Express"
    tracking_awb: str = "BLUEDART-IND-9382104"
    delivery_timestamp: str = "2026-08-28T14:32:00"
    otp_authenticated: bool = True
    three_ds_auth_success: bool = True

class DisputeDefenseResponse(BaseModel):
    dispute_id: str
    txn_id: str
    status: str
    win_probability_pct: float
    evidence_dossier: Dict[str, Any]
    markdown_defense_letter: str

class BenchmarkMetricsResponse(BaseModel):
    dataset_summary: Dict[str, Any]
    held_out_metrics: Dict[str, Any]
    unit_economics: Dict[str, Any]
    threshold_analysis: List[Dict[str, Any]]
    roc_curve: List[Dict[str, Any]]
