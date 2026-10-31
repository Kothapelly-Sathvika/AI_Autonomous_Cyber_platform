"""
Analytics – Plotly charts for threat intelligence and trends
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from core.database import get_incidents_df
from datetime import datetime, timedelta


def show_analytics():
    st.markdown("## 📊 Threat Analytics")
    st.markdown("---")

    df = get_incidents_df(5000)
    if df.empty:
        st.info("No data available yet. Start the simulator to generate analytics.")
        return

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["hour"] = df["timestamp"].dt.hour
    df["date"] = df["timestamp"].dt.date
    df["month"] = df["timestamp"].dt.to_period("M").astype(str)

    DARK_LAYOUT = dict(
        paper_bgcolor="#0d1117",
        plot_bgcolor="#0d1117",
        font_color="#c9d1d9",
        margin=dict(t=50, b=30, l=40, r=20),
    )

    # Row 1
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### ⏰ Threats by Hour")
        hourly = df.groupby("hour").size().reset_index(name="count")
        fig = px.bar(hourly, x="hour", y="count", color_discrete_sequence=["#58a6ff"])
        fig.update_layout(**DARK_LAYOUT, height=320)
        st.plotly_chart(fig, width="stretch")

    with c2:
        st.markdown("#### 📈 Threat Trend (Daily)")
        daily = df.groupby("date").size().reset_index(name="count")
        fig = px.line(daily, x="date", y="count", color_discrete_sequence=["#3fb950"], markers=True)
        fig.update_layout(**DARK_LAYOUT, height=320)
        st.plotly_chart(fig, width="stretch")

    # Row 2
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("#### 🎯 Top Attack Types")
        top = df["attack_type"].value_counts().head(10).reset_index()
        top.columns = ["attack_type", "count"]
        fig = px.bar(top, y="attack_type", x="count", orientation="h",
                     color="count", color_continuous_scale="blues")
        fig.update_layout(**DARK_LAYOUT, height=340)
        st.plotly_chart(fig, width="stretch")

    with c4:
        st.markdown("#### 🥧 Severity Distribution")
        sev = df["severity"].value_counts().reset_index()
        sev.columns = ["severity", "count"]
        fig = px.pie(sev, names="severity", values="count", hole=0.5,
                     color="severity",
                     color_discrete_map={"Low": "#3fb950", "Medium": "#d29922",
                                         "High": "#f78166", "Critical": "#f85149"})
        fig.update_layout(**DARK_LAYOUT, height=340)
        st.plotly_chart(fig, width="stretch")

    # Row 3
    c5, c6 = st.columns(2)
    with c5:
        st.markdown("#### 🌡️ Attack Heatmap (Hour × Day-of-Week)")
        df["dow"] = df["timestamp"].dt.day_name()
        hm = df.groupby(["dow", "hour"]).size().reset_index(name="count")
        dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        hm["dow"] = pd.Categorical(hm["dow"], categories=dow_order, ordered=True)
        hm = hm.sort_values("dow")
        fig = px.density_heatmap(hm, x="hour", y="dow", z="count",
                                 color_continuous_scale="YlOrRd")
        fig.update_layout(**DARK_LAYOUT, height=340)
        st.plotly_chart(fig, width="stretch")

    with c6:
        st.markdown("#### 🔝 Top Attacking IPs")
        ips = df["source_ip"].value_counts().head(10).reset_index()
        ips.columns = ["source_ip", "count"]
        fig = px.bar(ips, x="source_ip", y="count", color="count",
                     color_continuous_scale="reds")
        fig.update_layout(**DARK_LAYOUT, height=340, xaxis_tickangle=-45)
        st.plotly_chart(fig, width="stretch")

    # Row 4
    c7, c8 = st.columns(2)
    with c7:
        st.markdown("#### 🤖 AI Detection Accuracy")
        correct = (df["attack_type"] == df["ai_prediction"]).sum()
        total = len(df)
        acc = correct / total * 100 if total else 0
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=round(acc, 1),
                number={"suffix": "%"},
                gauge=dict(
                    axis=dict(range=[0, 100], tickcolor="#c9d1d9"),
                    bar=dict(color="#58a6ff"),
                    steps=[
                        dict(range=[0, 50], color="rgba(248,81,73,0.2)"),
                        dict(range=[50, 80], color="rgba(210,153,34,0.2)"),
                        dict(range=[80, 100], color="rgba(63,185,80,0.2)"),
                    ],
                ),
            )
        )
        fig.update_layout(**DARK_LAYOUT, height=300)
        st.plotly_chart(fig, width="stretch")

    with c8:
        st.markdown("#### 📅 Monthly Report")
        monthly = df.groupby("month").size().reset_index(name="count")
        fig = px.bar(monthly, x="month", y="count", color_discrete_sequence=["#bc8cff"])
        fig.update_layout(**DARK_LAYOUT, height=300)
        st.plotly_chart(fig, width="stretch")
