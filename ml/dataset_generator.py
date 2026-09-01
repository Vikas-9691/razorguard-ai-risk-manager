import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_synthetic_transactions(num_samples: int = 10000, seed: int = 42) -> pd.DataFrame:
    """
    Generates a realistic synthetic Indian BFSI & e-commerce transaction dataset with
    realistic feature distributions, noise, and borderline edge-cases.
    """
    random.seed(seed)
    np.random.seed(seed)

    base_time = datetime(2026, 1, 1, 0, 0, 0)
    data = []

    payment_modes = ["UPI", "CREDIT_CARD", "DEBIT_CARD", "NETBANKING", "COD", "WALLET", "BNPL"]
    payment_weights = [0.45, 0.22, 0.13, 0.08, 0.07, 0.03, 0.02]

    categories = ["ELECTRONICS", "JEWELLERY", "APPAREL", "GAMING_VOUCHER", "GROCERY", "TRAVEL_TICKET"]
    category_weights = [0.25, 0.08, 0.30, 0.12, 0.15, 0.10]

    delivery_types = ["STANDARD", "EXPRESS", "SAME_DAY"]
    delivery_weights = [0.65, 0.25, 0.10]

    cities = [
        ("Mumbai", "400001", "IN"),
        ("Bengaluru", "560001", "IN"),
        ("Delhi", "110001", "IN"),
        ("Hyderabad", "500001", "IN"),
        ("Chennai", "600001", "IN"),
        ("Kolkata", "700001", "IN"),
        ("Pune", "411001", "IN"),
        ("Jaipur", "302001", "IN"),
        ("Ahmedabad", "380001", "IN"),
        ("Surat", "395001", "IN")
    ]

    for i in range(num_samples):
        # 11.5% baseline fraud/abuse rate
        is_fraud = 1 if random.random() < 0.115 else 0

        txn_id = f"txn_{100000 + i}"
        cust_id = f"cust_{random.randint(1000, 4500)}"
        device_id = f"dev_{random.randint(500, 3000)}"
        
        txn_timestamp = base_time + timedelta(minutes=i * 3 + random.randint(0, 2))
        order_hour = txn_timestamp.hour

        city_info = random.choice(cities)
        delivery_city, pincode, dest_country = city_info

        # Add 6% random noise to introduce real-world edge cases & borderline ambiguity
        has_noise = random.random() < 0.06

        if is_fraud:
            fraud_type = random.choice([
                "CARD_STUFFING",
                "COD_RTO_ABUSE",
                "FRIENDLY_CHARGEBACK",
                "PROXY_ACCOUNT_TAKEOVER"
            ])

            if fraud_type == "CARD_STUFFING":
                amount = float(np.round(np.random.normal(32000, 12000), 2))
                amount = max(3500.0, amount)
                payment_mode = "CREDIT_CARD" if random.random() < 0.85 else "DEBIT_CARD"
                item_category = random.choice(["ELECTRONICS", "JEWELLERY", "GAMING_VOUCHER"])
                txn_velocity_1h = random.randint(2, 8) if not has_noise else 1
                txn_velocity_24h = txn_velocity_1h + random.randint(3, 10)
                device_fingerprint_entropy = round(random.uniform(0.15, 0.55), 2)
                ip_country = random.choice(["US", "NG", "RU", "ID", "IN"])
                ip_delivery_distance_km = round(random.uniform(250, 2800), 1)
                is_vpn_or_proxy = 1 if random.random() < 0.70 else 0
                user_account_age_days = random.randint(0, 25)
                historical_dispute_count = random.randint(0, 2)
                historical_rto_rate = round(random.uniform(0.0, 0.25), 2)
                card_bin_country_match = 0 if (ip_country != "IN" and random.random() < 0.75) else 1
                delivery_speed_type = "SAME_DAY" if random.random() < 0.55 else "EXPRESS"
                failed_attempts = random.randint(1, 4)

            elif fraud_type == "COD_RTO_ABUSE":
                amount = float(np.round(np.random.uniform(2000, 15000), 2))
                payment_mode = "COD"
                item_category = random.choice(["APPAREL", "ELECTRONICS"])
                txn_velocity_1h = random.randint(1, 4)
                txn_velocity_24h = txn_velocity_1h + random.randint(2, 6)
                device_fingerprint_entropy = round(random.uniform(0.25, 0.65), 2)
                ip_country = "IN"
                ip_delivery_distance_km = round(random.uniform(20, 450), 1)
                is_vpn_or_proxy = 0
                user_account_age_days = random.randint(0, 40)
                historical_dispute_count = random.randint(0, 1)
                historical_rto_rate = round(random.uniform(0.40, 0.90), 2)
                card_bin_country_match = 1
                delivery_speed_type = "STANDARD"
                failed_attempts = 0

            elif fraud_type == "FRIENDLY_CHARGEBACK":
                amount = float(np.round(np.random.uniform(4000, 38000), 2))
                payment_mode = random.choice(["CREDIT_CARD", "UPI", "BNPL"])
                item_category = random.choice(["GAMING_VOUCHER", "JEWELLERY", "TRAVEL_TICKET"])
                txn_velocity_1h = random.randint(1, 2)
                txn_velocity_24h = random.randint(1, 4)
                device_fingerprint_entropy = round(random.uniform(0.45, 0.75), 2)
                ip_country = "IN"
                ip_delivery_distance_km = round(random.uniform(5, 80), 1)
                is_vpn_or_proxy = 0
                user_account_age_days = random.randint(20, 240)
                historical_dispute_count = random.randint(1, 4)
                historical_rto_rate = round(random.uniform(0.05, 0.35), 2)
                card_bin_country_match = 1
                delivery_speed_type = "SAME_DAY" if random.random() < 0.6 else "EXPRESS"
                failed_attempts = random.randint(0, 1)

            else:  # PROXY_ACCOUNT_TAKEOVER
                amount = float(np.round(np.random.uniform(6000, 45000), 2))
                payment_mode = random.choice(["CREDIT_CARD", "NETBANKING"])
                item_category = random.choice(["ELECTRONICS", "TRAVEL_TICKET"])
                txn_velocity_1h = random.randint(2, 6)
                txn_velocity_24h = random.randint(4, 10)
                device_fingerprint_entropy = round(random.uniform(0.2, 0.5), 2)
                ip_country = random.choice(["US", "GB", "DE", "SG", "IN"])
                ip_delivery_distance_km = round(random.uniform(300, 3000), 1)
                is_vpn_or_proxy = 1 if random.random() < 0.85 else 0
                user_account_age_days = random.randint(60, 500)
                historical_dispute_count = 0
                historical_rto_rate = round(random.uniform(0.0, 0.10), 2)
                card_bin_country_match = 0 if ip_country != "IN" else 1
                delivery_speed_type = "EXPRESS"
                failed_attempts = random.randint(1, 3)

        else:
            # Legitimate transactions with realistic variance
            payment_mode = random.choices(payment_modes, weights=payment_weights)[0]
            item_category = random.choices(categories, weights=category_weights)[0]
            
            if item_category == "GROCERY":
                amount = float(np.round(np.random.exponential(scale=950) + 120, 2))
            elif item_category == "APPAREL":
                amount = float(np.round(np.random.exponential(scale=2400) + 450, 2))
            elif item_category == "ELECTRONICS":
                amount = float(np.round(np.random.exponential(scale=7500) + 900, 2))
            else:
                amount = float(np.round(np.random.exponential(scale=3200) + 350, 2))

            # Edge case: genuine customer buying a laptop or phone
            if has_noise and random.random() < 0.2:
                amount = float(np.round(np.random.uniform(25000, 65000), 2))

            # Normal velocity
            txn_velocity_1h = 1 if random.random() < 0.85 else random.randint(2, 3)
            txn_velocity_24h = txn_velocity_1h + (0 if random.random() < 0.65 else random.randint(1, 3))
            
            device_fingerprint_entropy = round(random.uniform(0.70, 0.99), 2) if not has_noise else round(random.uniform(0.45, 0.70), 2)
            ip_country = "IN" if random.random() < 0.98 else random.choice(["AE", "SG", "US"]) # Traveling genuine users
            ip_delivery_distance_km = round(random.uniform(1, 95), 1) if ip_country == "IN" else round(random.uniform(500, 2500), 1)
            is_vpn_or_proxy = 1 if random.random() < 0.04 else 0 # Work VPN
            user_account_age_days = random.randint(10, 1000)
            historical_dispute_count = 0 if random.random() < 0.95 else 1
            historical_rto_rate = round(random.uniform(0.0, 0.18), 2)
            card_bin_country_match = 1 if ip_country == "IN" else (0 if random.random() < 0.3 else 1)
            delivery_speed_type = random.choices(delivery_types, weights=delivery_weights)[0]
            failed_attempts = 0 if random.random() < 0.88 else random.randint(1, 2)

        data.append({
            "txn_id": txn_id,
            "timestamp": txn_timestamp.isoformat(),
            "customer_id": cust_id,
            "device_id": device_id,
            "amount": amount,
            "payment_mode": payment_mode,
            "item_category": item_category,
            "order_hour": order_hour,
            "delivery_speed_type": delivery_speed_type,
            "delivery_city": delivery_city,
            "pincode": pincode,
            "ip_country": ip_country,
            "ip_delivery_distance_km": ip_delivery_distance_km,
            "is_vpn_or_proxy": is_vpn_or_proxy,
            "txn_velocity_1h": txn_velocity_1h,
            "txn_velocity_24h": txn_velocity_24h,
            "device_fingerprint_entropy": device_fingerprint_entropy,
            "user_account_age_days": user_account_age_days,
            "historical_dispute_count": historical_dispute_count,
            "historical_rto_rate": historical_rto_rate,
            "card_bin_country_match": card_bin_country_match,
            "failed_attempts_before_success": failed_attempts,
            "label_is_fraud": is_fraud
        })

    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    df = generate_synthetic_transactions(10000)
    print(f"Generated {len(df)} transactions. Fraud rate: {df['label_is_fraud'].mean() * 100:.2f}%.")
