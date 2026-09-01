import os
import json
from datetime import datetime
from typing import List, Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app.models import TransactionModel, DisputeModel, AbuseClusterModel
from app.schemas import (
    TransactionScoreRequest, RiskScoreResponse,
    DisputeCreateRequest, DisputeDefenseResponse,
    BenchmarkMetricsResponse
)
from app.services.risk_engine import risk_engine
from app.services.abuse_sentinel import abuse_sentinel
from app.services.dispute_responder import dispute_responder

# Create DB tables
Base.metadata.create_all(bind=engine)

# ----------------- Seed Database Helper -----------------
def seed_initial_data():
    db = next(get_db())
    try:
        if db.query(TransactionModel).count() == 0:
            print("[DB] Seeding initial transactions and disputes...")
            sample_path = "ml/artifacts/sample_test_transactions.json"
            if os.path.exists(sample_path):
                with open(sample_path, "r") as f:
                    samples = json.load(f)

                for s in samples[:35]:
                    req = TransactionScoreRequest(**s)
                    res = risk_engine.score_transaction(req)
                    
                    txn_record = TransactionModel(
                        txn_id=res.txn_id,
                        customer_id=s.get("customer_id", "cust_101"),
                        device_id=s.get("device_id", "dev_501"),
                        amount=float(s.get("amount", 1000.0)),
                        payment_mode=s.get("payment_mode", "UPI"),
                        item_category=s.get("item_category", "APPAREL"),
                        delivery_city=s.get("delivery_city", "Bengaluru"),
                        pincode=s.get("pincode", "560001"),
                        ip_country=s.get("ip_country", "IN"),
                        is_vpn_or_proxy=bool(s.get("is_vpn_or_proxy", False)),
                        risk_score=res.risk_score,
                        risk_tier=res.risk_tier,
                        action=res.action,
                        top_risk_drivers=json.dumps([d.model_dump() for d in res.top_risk_drivers]),
                        risk_narrative=res.risk_narrative
                    )
                    db.add(txn_record)
            
            sample_disputes = [
                DisputeCreateRequest(
                    dispute_id="DSP_2026_0891",
                    txn_id="txn_107412",
                    amount=24999.0,
                    dispute_reason="10.4: Other Fraud - Card-Absent Environment",
                    bank_arn="ARN-94820194820194",
                    customer_name="Amitabh Sengupta",
                    customer_email="amitabh.s@example.com",
                    courier_name="BlueDart Express",
                    tracking_awb="BLUEDART-IND-749210",
                    delivery_timestamp="2026-08-25T16:14:00",
                    otp_authenticated=True,
                    three_ds_auth_success=True
                ),
                DisputeCreateRequest(
                    dispute_id="DSP_2026_0892",
                    txn_id="txn_107488",
                    amount=8450.0,
                    dispute_reason="13.1: Merchandise Not Received",
                    bank_arn="ARN-38291048201940",
                    customer_name="Pooja Sharma",
                    customer_email="pooja.sharma88@example.com",
                    courier_name="Delhivery",
                    tracking_awb="DELHIVERY-9920148",
                    delivery_timestamp="2026-08-27T11:45:00",
                    otp_authenticated=True,
                    three_ds_auth_success=True
                ),
                DisputeCreateRequest(
                    dispute_id="DSP_2026_0893",
                    txn_id="txn_107519",
                    amount=45200.0,
                    dispute_reason="10.4: Stolen Card Credential Claim",
                    bank_arn="ARN-11940294810293",
                    customer_name="Karan Malhotra",
                    customer_email="karan.m@example.com",
                    courier_name="DTDC Premium",
                    tracking_awb="DTDC-EXP-482019",
                    delivery_timestamp="2026-08-28T18:22:00",
                    otp_authenticated=True,
                    three_ds_auth_success=True
                )
            ]

            for d_req in sample_disputes:
                d_res = dispute_responder.generate_defense_package(d_req)
                disp_record = DisputeModel(
                    dispute_id=d_res.dispute_id,
                    txn_id=d_res.txn_id,
                    amount=d_req.amount,
                    dispute_reason=d_req.dispute_reason,
                    bank_arn=d_req.bank_arn,
                    customer_name=d_req.customer_name,
                    customer_email=d_req.customer_email,
                    status=d_res.status,
                    defense_package=json.dumps(d_res.model_dump())
                )
                db.add(disp_record)

            db.commit()
            print("[DB] Initial data seeded successfully.")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_initial_data()
    yield

app = FastAPI(
    title="RazorGuard AI - AI Risk Manager & Chargeback Defense",
    description="Defense-only AI Risk Management Platform for Razorpay merchants (Track 02)",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- API Endpoints -----------------

@app.post("/api/v1/risk/score", response_model=RiskScoreResponse)
def score_transaction_endpoint(req: TransactionScoreRequest, db: Session = Depends(get_db)):
    """
    Score incoming transaction in real-time, generate explainability drivers, and persist record.
    """
    res = risk_engine.score_transaction(req)
    
    txn_record = TransactionModel(
        txn_id=res.txn_id,
        customer_id=req.customer_id,
        device_id=req.device_id,
        amount=req.amount,
        payment_mode=req.payment_mode,
        item_category=req.item_category,
        delivery_city=req.delivery_city,
        pincode=req.pincode,
        ip_country=req.ip_country,
        is_vpn_or_proxy=req.is_vpn_or_proxy,
        risk_score=res.risk_score,
        risk_tier=res.risk_tier,
        action=res.action,
        top_risk_drivers=json.dumps([d.model_dump() for d in res.top_risk_drivers]),
        risk_narrative=res.risk_narrative
    )
    db.add(txn_record)
    db.commit()

    return res

@app.get("/api/v1/transactions")
def list_transactions(
    tier: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    List scored transactions with optional risk tier filter.
    """
    query = db.query(TransactionModel).order_by(TransactionModel.id.desc())
    if tier and tier.upper() != "ALL":
        query = query.filter(TransactionModel.risk_tier == tier.upper())
    
    records = query.limit(limit).all()
    results = []
    for r in records:
        results.append({
            "id": r.id,
            "txn_id": r.txn_id,
            "timestamp": r.timestamp.isoformat() if r.timestamp else "",
            "customer_id": r.customer_id,
            "amount": r.amount,
            "payment_mode": r.payment_mode,
            "item_category": r.item_category,
            "delivery_city": r.delivery_city,
            "risk_score": r.risk_score,
            "risk_tier": r.risk_tier,
            "action": r.action,
            "top_risk_drivers": json.loads(r.top_risk_drivers) if r.top_risk_drivers else [],
            "risk_narrative": r.risk_narrative
        })
    return results

@app.get("/api/v1/benchmark/metrics")
def get_benchmark_metrics():
    """
    Get held-out test evaluation metrics, confusion matrix, and threshold trade-off curve.
    """
    metrics_path = "ml/artifacts/benchmark_metrics.json"
    if not os.path.exists(metrics_path):
        from ml.train_and_eval import train_and_evaluate
        _, payload = train_and_evaluate(save_artifacts=True)
        return payload
    
    with open(metrics_path, "r") as f:
        data = json.load(f)
    return data

@app.get("/api/v1/disputes")
def list_disputes(db: Session = Depends(get_db)):
    """
    List active chargeback disputes and auto-generated defense packages.
    """
    disputes = db.query(DisputeModel).order_by(DisputeModel.id.desc()).all()
    results = []
    for d in disputes:
        results.append({
            "id": d.id,
            "dispute_id": d.dispute_id,
            "txn_id": d.txn_id,
            "amount": d.amount,
            "dispute_reason": d.dispute_reason,
            "bank_arn": d.bank_arn,
            "customer_name": d.customer_name,
            "customer_email": d.customer_email,
            "status": d.status,
            "defense_data": json.loads(d.defense_package) if d.defense_package else None,
            "created_at": d.created_at.isoformat() if d.created_at else ""
        })
    return results

@app.post("/api/v1/disputes/generate", response_model=DisputeDefenseResponse)
def generate_dispute_evidence(req: DisputeCreateRequest, db: Session = Depends(get_db)):
    """
    Auto-responder to assemble evidence and generate dispute rebuttal packet.
    """
    res = dispute_responder.generate_defense_package(req)
    
    record = DisputeModel(
        dispute_id=res.dispute_id,
        txn_id=res.txn_id,
        amount=req.amount,
        dispute_reason=req.dispute_reason,
        bank_arn=req.bank_arn,
        customer_name=req.customer_name,
        customer_email=req.customer_email,
        status=res.status,
        defense_package=json.dumps(res.model_dump())
    )
    db.add(record)
    db.commit()

    return res

@app.get("/api/v1/abuse-rings")
def get_abuse_rings():
    """
    Retrieve abuse ring clusters and entity relationship graph.
    """
    return abuse_sentinel.get_abuse_clusters()

@app.get("/api/v1/overview-stats")
def get_overview_stats(db: Session = Depends(get_db)):
    """
    Compute real-time summary statistics for dashboard header.
    """
    total_txns = db.query(TransactionModel).count()
    blocked_txns = db.query(TransactionModel).filter(TransactionModel.action == "BLOCK").count()
    high_risk_txns = db.query(TransactionModel).filter(TransactionModel.risk_tier.in_(["HIGH", "CRITICAL"])).count()
    
    total_amount = db.query(TransactionModel).all()
    total_volume_inr = sum(t.amount for t in total_amount)
    prevented_loss_inr = sum(t.amount for t in total_amount if t.action == "BLOCK")

    total_disputes = db.query(DisputeModel).count()
    defended_disputes = db.query(DisputeModel).filter(DisputeModel.status == "AUTO_DEFENDED").count()

    return {
        "total_scanned_transactions": total_txns,
        "total_volume_inr": round(total_volume_inr, 2),
        "fraud_blocked_count": blocked_txns,
        "prevented_loss_inr": round(prevented_loss_inr, 2),
        "high_risk_flagged_rate_pct": round((high_risk_txns / max(1, total_txns)) * 100, 2),
        "disputes_active": total_disputes,
        "disputes_auto_defended": defended_disputes,
        "auto_defense_rate_pct": round((defended_disputes / max(1, total_disputes)) * 100, 1)
    }

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
