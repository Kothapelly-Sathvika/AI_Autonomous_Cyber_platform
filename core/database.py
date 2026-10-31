"""
Database module – SQLite schema and helpers
"""
import sqlite3
import pandas as pd
from datetime import datetime
from utils.config import DB_PATH


def get_connection():
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'analyst',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1,
            is_verified INTEGER DEFAULT 0,
            verification_code TEXT,
            verification_expiry TIMESTAMP
        )
    """)

    # Migrate existing DBs – add columns if missing
    existing_cols = [r[1] for r in c.execute("PRAGMA table_info(users)").fetchall()]
    if "is_verified" not in existing_cols:
        c.execute("ALTER TABLE users ADD COLUMN is_verified INTEGER DEFAULT 0")
    if "verification_code" not in existing_cols:
        c.execute("ALTER TABLE users ADD COLUMN verification_code TEXT")
    if "verification_expiry" not in existing_cols:
        c.execute("ALTER TABLE users ADD COLUMN verification_expiry TIMESTAMP")
    # Mark all previously created users as verified (backward compat)
    c.execute("UPDATE users SET is_verified=1 WHERE is_verified IS NULL OR is_verified=0")

    # Threats / incidents table
    c.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id TEXT UNIQUE NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            attack_type TEXT,
            severity TEXT,
            source_ip TEXT,
            dest_ip TEXT,
            confidence REAL,
            description TEXT,
            status TEXT DEFAULT 'open',
            response_action TEXT,
            ai_prediction TEXT
        )
    """)

    # Blocked IPs
    c.execute("""
        CREATE TABLE IF NOT EXISTS blocked_ips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT UNIQUE NOT NULL,
            reason TEXT,
            blocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            blocked_by TEXT DEFAULT 'system'
        )
    """)

    # Threat intelligence
    c.execute("""
        CREATE TABLE IF NOT EXISTS threat_intel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            indicator TEXT NOT NULL,
            indicator_type TEXT NOT NULL,
            threat_level TEXT,
            source TEXT,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Audit log
    c.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user TEXT,
            action TEXT,
            details TEXT
        )
    """)

    # App settings
    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    # Email recipients
    c.execute("""
        CREATE TABLE IF NOT EXISTS email_recipients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            is_active INTEGER DEFAULT 1
        )
    """)

    conn.commit()

    # Seed default settings
    defaults = {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": "587",
        "smtp_email": "",
        "smtp_password": "",
        "alarm_enabled": "1",
        "auto_block": "1",
        "auto_email": "1",
        "simulation_speed": "3",
    }
    for k, v in defaults.items():
        c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))
    conn.commit()

    # Seed threat intel
    seed_intel = [
        ("192.168.1.100", "ip", "High", "internal_scan"),
        ("10.0.0.55", "ip", "Medium", "suspicious"),
        ("malware-c2.evil.com", "domain", "Critical", "c2_server"),
        ("phish-login.fake.com", "domain", "High", "phishing"),
        ("darkweb-market.onion", "domain", "Critical", "marketplace"),
        ("CN", "country", "Medium", "high_risk"),
        ("RU", "country", "Medium", "high_risk"),
        ("KP", "country", "High", "sanctioned"),
    ]
    for ind, itype, level, src in seed_intel:
        c.execute(
            "INSERT OR IGNORE INTO threat_intel (indicator, indicator_type, threat_level, source) VALUES (?,?,?,?)",
            (ind, itype, level, src),
        )
    conn.commit()
    conn.close()


# ── Helper functions ──────────────────────────────────────────

def log_audit(user, action, details=""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO audit_log (user, action, details) VALUES (?,?,?)",
        (user, action, details),
    )
    conn.commit()
    conn.close()


def get_setting(key, default=""):
    conn = get_connection()
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else default


def set_setting(key, value):
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES (?,?)", (key, value)
    )
    conn.commit()
    conn.close()


def block_ip(ip, reason="automated", blocked_by="system"):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO blocked_ips (ip, reason, blocked_by) VALUES (?,?,?)",
            (ip, reason, blocked_by),
        )
        conn.commit()
    finally:
        conn.close()


def unblock_ip(ip):
    conn = get_connection()
    conn.execute("DELETE FROM blocked_ips WHERE ip=?", (ip,))
    conn.commit()
    conn.close()


def is_ip_blocked(ip):
    conn = get_connection()
    row = conn.execute("SELECT 1 FROM blocked_ips WHERE ip=?", (ip,)).fetchone()
    conn.close()
    return row is not None


def get_blocked_ips_df():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM blocked_ips ORDER BY blocked_at DESC", conn)
    conn.close()
    return df


def get_incidents_df(limit=500):
    conn = get_connection()
    df = pd.read_sql(
        "SELECT * FROM incidents ORDER BY timestamp DESC LIMIT ?", conn, params=(limit,)
    )
    conn.close()
    return df


def insert_incident(incident_id, attack_type, severity, source_ip, dest_ip,
                    confidence, description, response_action, ai_prediction):
    conn = get_connection()
    conn.execute(
        """INSERT INTO incidents
           (incident_id, attack_type, severity, source_ip, dest_ip,
            confidence, description, response_action, ai_prediction)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (incident_id, attack_type, severity, source_ip, dest_ip,
         confidence, description, response_action, ai_prediction),
    )
    conn.commit()
    conn.close()


def get_threat_intel_df():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM threat_intel ORDER BY added_at DESC", conn)
    conn.close()
    return df


def add_threat_intel(indicator, indicator_type, threat_level, source):
    conn = get_connection()
    conn.execute(
        "INSERT INTO threat_intel (indicator, indicator_type, threat_level, source) VALUES (?,?,?,?)",
        (indicator, indicator_type, threat_level, source),
    )
    conn.commit()
    conn.close()


def get_audit_df(limit=200):
    conn = get_connection()
    df = pd.read_sql(
        "SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ?", conn, params=(limit,)
    )
    conn.close()
    return df
