# 🛡️ RazorGuard AI – Autonomous Risk Manager & Chargeback Defense

> **Razorpay AI Builder Internship 2026 Submission**  
> **Track 02: AI Risk Manager** — *Stop the merchant losing money to fraud, returns and chargebacks.*  
> **Constraint:** Strictly Defense-Only. Measured Precision & Recall on a Held-Out Test Set with Honest False-Positive Cost Accounting.

---

## 📌 Executive Summary

**RazorGuard AI** is a defense-only, production-grade AI risk management platform built for Indian BFSI & e-commerce merchants. It provides three layers of automated defense:
1. **Pre-Authorization ML Risk Scoring Engine**: Evaluates payment fraud, card credential stuffing, and COD Return-to-Origin (RTO) abuse before money is lost.
2. **Abuse Ring Sentinel**: Correlates device hardware hashes, VPN clusters, and card-hopping patterns into real-time syndicate graphs.
3. **Automated Chargeback Evidence Auto-Responder**: Instantly aggregates EMV 3DS authentication tokens, OTP delivery confirmations, and carrier tracking logs to generate legal representment rebuttal packets that win bank disputes.

---

## 📊 Held-Out Test Benchmark & Honest Unit Economics

Evaluated strictly on a **30% held-out test split (3,000 unseen transactions)** from a 10,000-sample benchmark dataset modeling Indian e-commerce transaction patterns (UPI, RuPay/Visa/Mastercard, COD, Netbanking, BNPL):

| Metric | Measured Benchmark | Description |
| :--- | :--- | :--- |
| **Precision** | **99.16%** | High accuracy ensuring genuine customers are not falsely blocked |
| **Recall** | **99.44%** | Successfully intercepts almost all simulated fraud & RTO abuse cases |
| **F1-Score** | **99.30%** | Harmonic balance between precision and recall |
| **ROC-AUC** | **1.0000** | Exceptional class separability across risk tiers |
| **False Positive Rate (FPR)** | **0.11%** | Minimal friction on legitimate purchasing traffic |
| **Gross Fraud Prevented** | **₹3,009,000** | 354 confirmed fraud attempts stopped |
| **False Positive Cost** | **₹1,350** | 3 genuine customers subjected to verification friction (at ₹450/event) |
| **Net Realized Value** | **₹3,007,650** | Net financial value delivered to the merchant |

---

## 🏗️ System Architecture

```
                                  ┌────────────────────────────────────────┐
                                  │      RazorGuard Web Dashboard UI       │
                                  │   (Live Simulator, Metrics, Disputes)  │
                                  └───────────────────▲────────────────────┘
                                                      │ REST APIs
┌─────────────────────────────────────────────────────▼──────────────────────────────────────────────────┐
│                                       FastAPI Backend Service                                          │
│                                                                                                        │
│  ┌──────────────────────────┐   ┌─────────────────────────┐   ┌─────────────────────────────────────┐  │
│  │   ML Risk Classifier     │   │  Abuse Ring Sentinel    │   │  Chargeback Evidence Auto-Responder │  │
│  │ (RandomForest/Ensemble)  │   │  (Velocity & Entity     │   │  (Dossier packager with 3DS, POD,   │  │
│  │ Precision, Recall, AUC   │   │   Graph Clustering)     │   │   IP, and OTP audit trail)          │  │
│  └─────────────▲────────────┘   └────────────▲────────────┘   └──────────────────▲──────────────────┘  │
│                │                             │                                   │                     │
│  ┌─────────────┴────────────┐   ┌────────────┴────────────┐                      │                     │
│  │  Held-Out Benchmark Set  │   │  False Positive Engine  │                      │                     │
│  │  (30% Chronological split│   │ (Unit economic friction │                      │                     │
│  │   10,000+ synthetic txn) │   │  vs. fraud loss saved)  │                      │                     │
│  └──────────────────────────┘   └─────────────────────────┘                      │                     │
└──────────────────────────────────────────────┬───────────────────────────────────┴─────────────────────┘
                                               │
                                  ┌────────────▼───────────┐
                                  │ SQLite / Database Log  │
                                  │ (Transactions, Disputes)
                                  └────────────────────────┘
```

---

## 🚀 Quick Start (Run with 1 Command)

### Prerequisites
- Python 3.10+ (Tested on Python 3.13)

### Installation & Launch

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start RazorGuard AI**:
   ```bash
   python run.py
   ```

3. **Open the Web Dashboard**:
   The dashboard automatically opens in your browser at:
   `http://127.0.0.1:8000`

---

## 🧪 Running Automated Tests

Run the complete test suite:
```bash
python -m pytest tests/ -v
```

All unit and integration tests verify:
- Real-time transaction risk scoring & explainability drivers
- Multi-layer defense heuristics
- Chargeback evidence auto-responder & dossier generation
- REST API endpoints and data persistence

---

## 🌐 API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/risk/score` | Score transaction in real-time with explainable drivers |
| `GET` | `/api/v1/transactions` | Query transaction intelligence ledger |
| `GET` | `/api/v1/benchmark/metrics` | Retrieve held-out test benchmark metrics & threshold curves |
| `GET` | `/api/v1/disputes` | List active chargeback disputes |
| `POST` | `/api/v1/disputes/generate` | Auto-generate formal rebuttal evidence dossier |
| `GET` | `/api/v1/abuse-rings` | Return fraud ring clusters and network graph nodes |
| `GET` | `/api/v1/overview-stats` | Compute real-time dashboard KPIs |

---

## 📁 Project Structure

```
razorguard-ai-risk-manager/
├── ml/
│   ├── dataset_generator.py      # Synthetic Indian BFSI/e-commerce data generator
│   ├── train_and_eval.py         # ML training, held-out evaluation & false positive economics
│   └── artifacts/                # Serialized model & benchmark JSON outputs
├── app/
│   ├── main.py                   # FastAPI application & REST endpoints
│   ├── database.py               # SQLite / SQLAlchemy configuration
│   ├── models.py                 # ORM database models
│   ├── schemas.py                # Pydantic v2 schemas
│   ├── services/
│   │   ├── risk_engine.py        # Real-time scoring & explainability engine
│   │   ├── abuse_sentinel.py     # Fraud ring graph clustering
│   │   └── dispute_responder.py  # Chargeback rebuttal evidence auto-responder
│   └── static/
│       ├── index.html            # Single-page web dashboard
│       ├── app.js                # Frontend controller & interactive charts
│       └── style.css             # Glassmorphism & dark theme styles
├── tests/
│   ├── test_risk_engine.py       # Unit tests for ML & heuristic scoring
│   ├── test_dispute_responder.py # Unit tests for evidence compilation
│   └── test_api.py               # Integration tests for FastAPI endpoints
├── run.py                        # Single-command launcher script
├── requirements.txt              # Project dependencies
├── README.md                     # Documentation

```
