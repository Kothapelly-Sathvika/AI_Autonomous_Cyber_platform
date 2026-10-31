"""
Configuration module for Autonomous AI Cyber Defense Platform
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Database
DB_PATH = DATA_DIR / "cyberdefense.db"

# CSV logs
LOG_PATH = DATA_DIR / "threat_logs.csv"

# Email defaults (override via Settings UI)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
DEFAULT_ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@example.com")

# Threat severity levels
SEVERITY_LEVELS = ["Low", "Medium", "High", "Critical"]

# Attack types
ATTACK_TYPES = [
    "Malware", "Ransomware", "DDoS", "Brute Force", "SQL Injection",
    "XSS", "Phishing", "Insider Threat", "Credential Theft", "Port Scan",
    "Spam"
]

# App metadata
APP_TITLE = "Autonomous AI Cyber Defense Platform"
APP_ICON = "🛡️"
APP_VERSION = "1.0.0"
