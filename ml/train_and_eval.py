import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
    average_precision_score, confusion_matrix, roc_curve
)
from ml.dataset_generator import generate_synthetic_transactions

NUMERICAL_FEATURES = [
    "amount",
    "order_hour",
    "ip_delivery_distance_km",
    "txn_velocity_1h",
    "txn_velocity_24h",
    "device_fingerprint_entropy",
    "user_account_age_days",
    "historical_dispute_count",
    "historical_rto_rate",
    "failed_attempts_before_success",
    "is_vpn_or_proxy",
    "card_bin_country_match"
]

CATEGORICAL_FEATURES = [
    "payment_mode",
    "item_category",
    "delivery_speed_type",
    "ip_country"
]

def build_model_pipeline():
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERICAL_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_FEATURES)
        ]
    )

    rf_clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )

    gb_clf = GradientBoostingClassifier(
        n_estimators=80,
        learning_rate=0.08,
        max_depth=4,
        random_state=42
    )

    ensemble = VotingClassifier(
        estimators=[
            ("rf", rf_clf),
            ("gb", gb_clf)
        ],
        voting="soft"
    )

    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", ensemble)
    ])

    return pipeline

def train_and_evaluate(dataset_size: int = 10000, save_artifacts: bool = True):
    print("=" * 60)
    print("RazorGuard AI - Training & Held-Out Benchmark Evaluation")
    print("=" * 60)

    # 1. Generate dataset
    df = generate_synthetic_transactions(num_samples=dataset_size, seed=42)
    print(f"Dataset generated: {len(df)} total transactions.")
    print(f"Overall Fraud / High-Risk Distribution: {df['label_is_fraud'].sum()} cases ({df['label_is_fraud'].mean()*100:.2f}%)")

    # 2. Strict Chronological Split (70% Train, 30% Held-Out Test)
    split_idx = int(len(df) * 0.70)
    train_df = df.iloc[:split_idx].copy()
    test_df = df.iloc[split_idx:].copy()

    X_train = train_df[NUMERICAL_FEATURES + CATEGORICAL_FEATURES]
    y_train = train_df["label_is_fraud"]

    X_test = test_df[NUMERICAL_FEATURES + CATEGORICAL_FEATURES]
    y_test = test_df["label_is_fraud"]

    print(f"Training set size: {len(X_train)} | Held-Out Test set size: {len(X_test)}")

    # 3. Fit pipeline on training data ONLY
    pipeline = build_model_pipeline()
    pipeline.fit(X_train, y_train)
    print("Model training completed successfully.")

    # 4. Predict probabilities on Held-Out Test set
    y_prob = pipeline.predict_proba(X_test)[:, 1]
    
    # Default operational decision threshold: 0.50
    default_threshold = 0.50
    y_pred = (y_prob >= default_threshold).astype(int)

    # 5. Calculate Metrics on Held-Out Test Set
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    roc_auc = float(roc_auc_score(y_test, y_prob))
    pr_auc = float(average_precision_score(y_test, y_prob))

    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
    fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0

    print("\n--- Held-Out Test Set Results ---")
    print(f"Precision: {prec * 100:.2f}%")
    print(f"Recall:    {rec * 100:.2f}%")
    print(f"F1-Score:  {f1 * 100:.2f}%")
    print(f"ROC-AUC:   {roc_auc:.4f}")
    print(f"PR-AUC:    {pr_auc:.4f}")
    print(f"Confusion Matrix: TP={tp}, FP={fp}, TN={tn}, FN={fn}")
    print(f"False Positive Rate (FPR): {fpr * 100:.2f}%")

    # 6. Unit Economics & False Positive Cost Accounting
    avg_fraud_saved_per_tp = 8500.0
    fp_friction_cost = 450.0

    gross_fraud_prevented = tp * avg_fraud_saved_per_tp
    total_fp_cost = fp * fp_friction_cost
    net_savings = gross_fraud_prevented - total_fp_cost

    print("\n--- Financial Unit Economics (Test Set 3,000 txns) ---")
    print(f"Gross Fraud Losses Prevented: INR {gross_fraud_prevented:,.2f}")
    print(f"False Positive Friction Cost: INR {total_fp_cost:,.2f}")
    print(f"Net Realized Merchant Value:  INR {net_savings:,.2f}")

    # 7. Compute Threshold Curve for Interactive Dashboard Simulator
    threshold_analysis = []
    for thresh in np.linspace(0.10, 0.90, 17):
        t = round(float(thresh), 2)
        preds_t = (y_prob >= t).astype(int)
        t_tn, t_fp, t_fn, t_tp = confusion_matrix(y_test, preds_t).ravel()
        t_prec = float(precision_score(y_test, preds_t, zero_division=0))
        t_rec = float(recall_score(y_test, preds_t, zero_division=0))
        t_f1 = float(f1_score(y_test, preds_t, zero_division=0))
        t_saved = float(t_tp * avg_fraud_saved_per_tp)
        t_fp_cost = float(t_fp * fp_friction_cost)
        t_net = float(t_saved - t_fp_cost)

        threshold_analysis.append({
            "threshold": t,
            "precision": round(t_prec * 100, 2),
            "recall": round(t_rec * 100, 2),
            "f1_score": round(t_f1 * 100, 2),
            "tp": int(t_tp),
            "fp": int(t_fp),
            "tn": int(t_tn),
            "fn": int(t_fn),
            "gross_saved_inr": round(t_saved, 2),
            "fp_cost_inr": round(t_fp_cost, 2),
            "net_benefit_inr": round(t_net, 2)
        })

    fpr_arr, tpr_arr, _ = roc_curve(y_test, y_prob)
    step = max(1, len(fpr_arr) // 25)
    roc_points = [
        {"fpr": round(float(f), 4), "tpr": round(float(t), 4)}
        for f, t in zip(fpr_arr[::step], tpr_arr[::step])
    ]

    metrics_payload = {
        "dataset_summary": {
            "total_samples": len(df),
            "train_samples": len(train_df),
            "test_samples": len(test_df),
            "fraud_rate_pct": round(float(df["label_is_fraud"].mean() * 100), 2)
        },
        "held_out_metrics": {
            "default_threshold": default_threshold,
            "precision": round(prec * 100, 2),
            "recall": round(rec * 100, 2),
            "f1_score": round(f1 * 100, 2),
            "roc_auc": round(roc_auc, 4),
            "pr_auc": round(pr_auc, 4),
            "false_positive_rate": round(fpr * 100, 2),
            "confusion_matrix": {
                "tp": int(tp),
                "fp": int(fp),
                "tn": int(tn),
                "fn": int(fn)
            }
        },
        "unit_economics": {
            "avg_fraud_saved_per_tp": avg_fraud_saved_per_tp,
            "fp_friction_cost": fp_friction_cost,
            "gross_saved_inr": round(gross_fraud_prevented, 2),
            "fp_cost_inr": round(total_fp_cost, 2),
            "net_savings_inr": round(net_savings, 2)
        },
        "threshold_analysis": threshold_analysis,
        "roc_curve": roc_points
    }

    if save_artifacts:
        os.makedirs("ml/artifacts", exist_ok=True)
        model_path = "ml/artifacts/razorguard_model.joblib"
        metrics_path = "ml/artifacts/benchmark_metrics.json"
        
        joblib.dump(pipeline, model_path)
        with open(metrics_path, "w") as f:
            json.dump(metrics_payload, f, indent=2)

        sample_test_path = "ml/artifacts/sample_test_transactions.json"
        sample_test_records = test_df.head(60).to_dict(orient="records")
        with open(sample_test_path, "w") as f:
            json.dump(sample_test_records, f, indent=2)

        print(f"\nArtifacts saved successfully to {model_path} and {metrics_path}")

    return pipeline, metrics_payload

if __name__ == "__main__":
    train_and_evaluate(10000, save_artifacts=True)
