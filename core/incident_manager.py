"""
Incident Manager – CRUD, search, export for security incidents
"""
import csv
import io
import pandas as pd
from core.database import get_connection, get_incidents_df


def search_incidents(query: str = "", severity: str = "All", status: str = "All", limit: int = 500):
    df = get_incidents_df(limit)
    if df.empty:
        return df
    if severity != "All":
        df = df[df["severity"] == severity]
    if status != "All":
        df = df[df["status"] == status]
    if query:
        mask = (
            df["incident_id"].str.contains(query, case=False, na=False)
            | df["attack_type"].str.contains(query, case=False, na=False)
            | df["source_ip"].str.contains(query, case=False, na=False)
            | df["description"].str.contains(query, case=False, na=False)
        )
        df = df[mask]
    return df


def update_incident_status(incident_id: str, new_status: str):
    conn = get_connection()
    conn.execute(
        "UPDATE incidents SET status=? WHERE incident_id=?", (new_status, incident_id)
    )
    conn.commit()
    conn.close()


def export_csv(df: pd.DataFrame) -> str:
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue()


def get_stats():
    df = get_incidents_df(5000)
    if df.empty:
        return {"total": 0, "critical": 0, "high": 0, "open": 0, "resolved": 0}
    return {
        "total": len(df),
        "critical": int((df["severity"] == "Critical").sum()),
        "high": int((df["severity"] == "High").sum()),
        "medium": int((df["severity"] == "Medium").sum()),
        "low": int((df["severity"] == "Low").sum()),
        "open": int((df["status"] == "open").sum()),
        "resolved": int((df["status"] == "resolved").sum()),
    }
