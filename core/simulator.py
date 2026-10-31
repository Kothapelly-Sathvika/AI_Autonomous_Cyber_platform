"""
Attack Simulator – generates realistic cyber attack events for the dashboard
"""
import random
import uuid
from datetime import datetime
import numpy as np
from utils.config import ATTACK_TYPES

# Realistic IP pools
EXTERNAL_IPS = [
    "45.33.32.156", "185.220.101.34", "91.219.236.222", "198.51.100.78",
    "203.0.113.42", "172.16.0.5", "10.0.0.15", "192.168.1.100",
    "85.214.132.117", "177.54.150.200", "103.224.182.250", "5.188.210.101",
    "194.26.29.113", "23.129.64.210", "171.25.193.77", "62.102.148.68",
]
INTERNAL_IPS = [
    "192.168.1.10", "192.168.1.20", "192.168.1.30", "10.0.0.1",
    "10.0.0.2", "172.16.0.100", "172.16.0.101",
]
USERNAMES = [
    "admin", "root", "jsmith", "deploy", "service_acct", "dbadmin",
    "operator", "guest", "testuser", "backup_svc",
]
EVENT_TYPES = [
    "Login Attempt", "Failed Login", "Packet Anomaly", "Malware Event",
    "Suspicious Process", "Unauthorized Access", "Port Scan",
    "SQL Injection", "Brute Force", "Phishing", "Ransomware", "DDoS",
    "Spam Detected",
]

_DESCRIPTIONS = {
    "Malware": "Trojan horse payload detected in inbound traffic",
    "Ransomware": "AES-256 file encryption behaviour observed on endpoint",
    "DDoS": "Volumetric SYN flood targeting web server",
    "Brute Force": "Multiple failed authentication attempts from single source",
    "SQL Injection": "Malicious SQL payload in HTTP parameter",
    "XSS": "Reflected cross-site scripting attempt in form input",
    "Phishing": "Credential harvesting page mimicking corporate SSO",
    "Insider Threat": "Anomalous data exfiltration by internal user",
    "Credential Theft": "Pass-the-hash attempt on domain controller",
    "Port Scan": "Sequential port probing detected from external host",
    "Spam": "Bulk unsolicited message with suspicious payload and embedded links",
}


def generate_event() -> dict:
    """Generate a single simulated network / security event."""
    attack = random.choice(ATTACK_TYPES)
    src_ip = random.choice(EXTERNAL_IPS)
    dst_ip = random.choice(INTERNAL_IPS)
    event_type = random.choice(EVENT_TYPES)

    # Feature vector for AI analysis
    features = {
        "packets_per_sec": int(np.random.exponential(300)),
        "failed_logins": int(np.random.poisson(8)),
        "payload_size": int(np.random.exponential(3000)),
        "unique_ports": int(np.random.poisson(15)),
        "entropy": round(random.uniform(1.0, 8.0), 2),
    }

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "event_type": event_type,
        "source_ip": src_ip,
        "dest_ip": dst_ip,
        "username": random.choice(USERNAMES),
        "attack_type": attack,
        "description": _DESCRIPTIONS.get(attack, "Suspicious activity detected"),
        "features": features,
        "incident_id": f"INC-{uuid.uuid4().hex[:8].upper()}",
    }


def generate_batch(n: int = 10) -> list:
    return [generate_event() for _ in range(n)]
