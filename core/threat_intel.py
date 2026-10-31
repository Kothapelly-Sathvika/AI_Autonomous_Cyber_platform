"""
Threat Intelligence – compare traffic against known-bad indicators
"""
from core.database import get_connection, get_threat_intel_df, add_threat_intel as _add


def check_ip(ip: str) -> dict | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM threat_intel WHERE indicator=? AND indicator_type='ip'", (ip,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def check_domain(domain: str) -> dict | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM threat_intel WHERE indicator=? AND indicator_type='domain'", (domain,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_intel():
    return get_threat_intel_df()


def add_intel(indicator: str, indicator_type: str, threat_level: str, source: str):
    _add(indicator, indicator_type, threat_level, source)
