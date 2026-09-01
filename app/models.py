from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class TransactionModel(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    txn_id = Column(String(64), unique=True, index=True, nullable=False)
    timestamp = Column(DateTime, default=func.now())
    customer_id = Column(String(64), index=True)
    device_id = Column(String(64), index=True)
    amount = Column(Float, nullable=False)
    payment_mode = Column(String(32), nullable=False)
    item_category = Column(String(64), nullable=False)
    delivery_city = Column(String(64))
    pincode = Column(String(16))
    ip_country = Column(String(8))
    is_vpn_or_proxy = Column(Boolean, default=False)
    
    # Risk Results
    risk_score = Column(Float, nullable=False)  # 0 to 100
    risk_tier = Column(String(16), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    action = Column(String(32), nullable=False)  # ALLOW, STEP_UP_2FA, MANUAL_REVIEW, BLOCK
    top_risk_drivers = Column(Text)  # JSON string of contributing risk factors
    risk_narrative = Column(Text)  # Underwriting explanation

class DisputeModel(Base):
    __tablename__ = "disputes"

    id = Column(Integer, primary_key=True, index=True)
    dispute_id = Column(String(64), unique=True, index=True, nullable=False)
    txn_id = Column(String(64), index=True, nullable=False)
    amount = Column(Float, nullable=False)
    dispute_reason = Column(String(128), nullable=False)
    bank_arn = Column(String(64))
    customer_name = Column(String(128))
    customer_email = Column(String(128))
    status = Column(String(32), default="ACTION_REQUIRED")  # ACTION_REQUIRED, AUTO_DEFENDED, WON, LOST
    defense_package = Column(Text)  # JSON string of compiled legal defense dossier
    created_at = Column(DateTime, default=func.now())

class AbuseClusterModel(Base):
    __tablename__ = "abuse_clusters"

    id = Column(Integer, primary_key=True, index=True)
    cluster_id = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(128), nullable=False)
    risk_level = Column(String(16), nullable=False)
    device_count = Column(Integer, default=1)
    user_count = Column(Integer, default=1)
    txn_count = Column(Integer, default=1)
    total_loss_at_risk = Column(Float, default=0.0)
    primary_vector = Column(String(64))
    entities_json = Column(Text)  # JSON representation of nodes and edges
    created_at = Column(DateTime, default=func.now())
