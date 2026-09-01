from typing import Dict, Any, List
import json
from datetime import datetime

class AbuseSentinel:
    """
    Abuse Ring Sentinel detects coordinated fraud rings, device multiplexing,
    and velocity spikes across the merchant network.
    """

    def get_abuse_clusters(self) -> Dict[str, Any]:
        """
        Returns detected abuse clusters and visual network graph structure for the UI.
        """
        clusters = [
            {
                "cluster_id": "RING-891",
                "name": "Mumbai Device Multiplexing Ring",
                "risk_level": "CRITICAL",
                "device_count": 1,
                "user_count": 8,
                "txn_count": 23,
                "total_loss_at_risk": 184500.0,
                "primary_vector": "Shared Device Hardware Hash across 8 new accounts within 4 hours",
                "confidence_score": 96.4,
                "recommended_action": "Blacklist Device Hardware Fingerprint dev_891 & freeze linked accounts"
            },
            {
                "cluster_id": "RING-402",
                "name": "NCR COD RTO Abuse Syndicate",
                "risk_level": "HIGH",
                "device_count": 4,
                "user_count": 12,
                "txn_count": 31,
                "total_loss_at_risk": 98200.0,
                "primary_vector": "Coordinated COD electronics orders with 92% historical refusal at doorstep",
                "confidence_score": 91.8,
                "recommended_action": "Require pre-payment (UPI/Card) for PIN codes 110092, 110095"
            },
            {
                "cluster_id": "RING-119",
                "name": "International Proxy Card Hopping",
                "risk_level": "CRITICAL",
                "device_count": 3,
                "user_count": 5,
                "txn_count": 14,
                "total_loss_at_risk": 245000.0,
                "primary_vector": "US/Nigeria VPN exit nodes testing compromised Visa BINs (4111xx, 4242xx)",
                "confidence_score": 98.2,
                "recommended_action": "Trigger strict mandatory 3DS Step-up for all non-IN IPs"
            }
        ]

        # Generate Graph Nodes and Edges for UI visualization
        nodes = []
        edges = []

        # Ring 891 Nodes
        nodes.append({"id": "dev_891", "label": "Device: dev_891 (Anchor)", "group": "device", "color": "#ef4444", "size": 25})
        for i in range(1, 7):
            u_id = f"cust_891_{i}"
            nodes.append({"id": u_id, "label": f"User: {u_id}", "group": "user", "color": "#f97316", "size": 15})
            edges.append({"from": "dev_891", "to": u_id, "label": "shared_device"})
            
            t_id = f"txn_891_{i}"
            nodes.append({"id": t_id, "label": f"Txn: INR {15000 + i*2500}", "group": "transaction", "color": "#eab308", "size": 10})
            edges.append({"from": u_id, "to": t_id, "label": "placed_order"})

        # Ring 119 Nodes
        nodes.append({"id": "vpn_us_east", "label": "IP: 198.51.100.42 (US VPN)", "group": "ip", "color": "#dc2626", "size": 22})
        for i in range(1, 4):
            u_id = f"cust_vpn_{i}"
            nodes.append({"id": u_id, "label": f"User: {u_id}", "group": "user", "color": "#f97316", "size": 14})
            edges.append({"from": "vpn_us_east", "to": u_id, "label": "vpn_tunnel"})
            
            card_id = f"card_bin_4111_{i}"
            nodes.append({"id": card_id, "label": f"Card: **** 411{i}", "group": "card", "color": "#8b5cf6", "size": 12})
            edges.append({"from": u_id, "to": card_id, "label": "used_card"})

        return {
            "summary": {
                "active_rings_detected": len(clusters),
                "total_entities_flagged": len(nodes),
                "aggregate_exposure_inr": sum(c["total_loss_at_risk"] for c in clusters)
            },
            "clusters": clusters,
            "network_graph": {
                "nodes": nodes,
                "edges": edges
            }
        }

abuse_sentinel = AbuseSentinel()
