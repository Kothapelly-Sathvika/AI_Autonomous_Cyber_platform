"""
Dashboard – KPI cards, gauges, live counters
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.database import get_incidents_df, get_blocked_ips_df, get_connection
import psutil
from datetime import datetime


def _kpi_card(icon, label, value, color="#58a6ff"):
    st.markdown(
        f"""
        <div style="
            background:linear-gradient(135deg,#0d1117,#161b22);
            border:1px solid #30363d; border-radius:12px; padding:1.2rem;
            text-align:center; box-shadow:0 0 15px {color}22;
            transition:transform .2s;
        "
        onmouseover="this.style.transform='scale(1.04)'"
        onmouseout="this.style.transform='scale(1)'">
            <div style="font-size:2rem">{icon}</div>
            <div style="font-size:1.8rem;font-weight:700;color:{color}">{value}</div>
            <div style="color:#8b949e;font-size:.85rem">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_dashboard():
    st.markdown("## 🎯 Command Dashboard")
    st.markdown("---")

    df = get_incidents_df(1000)
    blocked = get_blocked_ips_df()

    today = datetime.now().strftime("%Y-%m-%d")
    today_count = 0
    crit_count = 0
    if not df.empty and "timestamp" in df.columns:
        df["date"] = pd.to_datetime(df["timestamp"], errors="coerce").dt.date.astype(str)
        today_count = int((df["date"] == today).sum())
        crit_count = int((df["severity"] == "Critical").sum())

    total = len(df) if not df.empty else 0
    blocked_count = len(blocked) if not blocked.empty else 0
    avg_conf = round(df["confidence"].mean() * 100, 1) if not df.empty and "confidence" in df.columns else 0

    # Row 1 – KPI cards
    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
    with c1:
        _kpi_card("🛡️", "Total Threats", total, "#58a6ff")
    with c2:
        _kpi_card("🔴", "Critical", crit_count, "#f85149")
    with c3:
        _kpi_card("🟡", "Today's Attacks", today_count, "#d29922")
    with c4:
        _kpi_card("🚫", "Blocked IPs", blocked_count, "#f78166")
    with c5:
        _kpi_card("🟢", "Active Sessions", st.session_state.get("active_sessions", 1), "#3fb950")
    with c6:
        _kpi_card("🎯", "Detection %", f"{avg_conf}%", "#bc8cff")
    with c7:
        _kpi_card("🤖", "AI Confidence", f"{avg_conf}%", "#79c0ff")

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 2 – Gauges and resource monitors
    col_left, col_right = st.columns([2, 1])

    with col_left:
        if not df.empty and "severity" in df.columns:
            sev_counts = df["severity"].value_counts()
            fig = go.Figure(
                go.Pie(
                    labels=sev_counts.index.tolist(),
                    values=sev_counts.values.tolist(),
                    hole=0.55,
                    marker=dict(colors=["#3fb950", "#d29922", "#f78166", "#f85149"]),
                )
            )
            fig.update_layout(
                title="Severity Distribution",
                paper_bgcolor="#0d1117",
                plot_bgcolor="#0d1117",
                font_color="#c9d1d9",
                height=340,
                margin=dict(t=40, b=20, l=20, r=20),
            )
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("No incidents yet. The simulator will populate the dashboard shortly.")

    with col_right:
        st.markdown("#### 💻 System Resources")
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent if hasattr(psutil.disk_usage("/"), "percent") else 0

        for label, val, clr in [("CPU", cpu, "#58a6ff"), ("RAM", ram, "#3fb950"), ("Disk", disk, "#d29922")]:
            st.markdown(f"**{label}**")
            st.progress(val / 100)
            st.caption(f"{val}%")

        st.markdown("---")
        st.markdown(f"🕐 **{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**")
        st.markdown("🟢 **Network Status:** Online")

    # Row 3 – Recent activity
    st.markdown("### 📋 Recent Threats")
    if not df.empty:
        display_cols = ["timestamp", "incident_id", "attack_type", "severity", "source_ip", "confidence"]
        available = [c for c in display_cols if c in df.columns]
        st.dataframe(df[available].head(20), width="stretch", hide_index=True)
    else:
        st.info("Awaiting threat data…")
