"""
Threat Detection – manual analysis and AI inspection page
"""
import streamlit as st
import numpy as np
from core.threat_detection import ThreatDetector
from core.threat_intel import check_ip


@st.cache_resource
def _get_detector():
    return ThreatDetector()


def show_detection():
    st.markdown("## 🧠 AI Threat Detection")
    st.markdown("---")

    detector = _get_detector()

    st.markdown("### Manual Analysis")
    st.markdown("Enter network traffic features to analyse with the AI model:")

    with st.form("manual_detect"):
        c1, c2 = st.columns(2)
        pps = c1.number_input("Packets per second", 0, 10000, 100)
        failed = c1.number_input("Failed login attempts", 0, 500, 0)
        payload = c2.number_input("Payload size (bytes)", 0, 50000, 500)
        ports = c2.number_input("Unique destination ports", 0, 1000, 3)
        entropy = st.slider("Payload entropy (0-8)", 0.0, 8.0, 3.0, 0.1)
        src_ip = st.text_input("Source IP (optional – for threat intel check)")

        submitted = st.form_submit_button("🔍 Analyse with AI", width="stretch")

    if submitted:
        features = {
            "packets_per_sec": pps,
            "failed_logins": failed,
            "payload_size": payload,
            "unique_ports": ports,
            "entropy": entropy,
        }
        result = detector.analyze(features)

        st.markdown("---")
        st.markdown("### AI Analysis Result")

        # Severity badge colours
        sev_colors = {"Low": "#3fb950", "Medium": "#d29922", "High": "#f78166", "Critical": "#f85149"}
        sev_clr = sev_colors.get(result["severity"], "#8b949e")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Anomaly Detected", "Yes" if result["is_anomaly"] else "No")
        c2.markdown(f"**Attack Type:** {result['attack_type']}")
        c3.markdown(
            f"**Severity:** <span style='color:{sev_clr};font-weight:bold'>{result['severity']}</span>",
            unsafe_allow_html=True,
        )
        c4.metric("Confidence", f"{result['confidence']:.1%}")

        # Confidence gauge
        import plotly.graph_objects as go
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=result["confidence"] * 100,
                number={"suffix": "%"},
                gauge=dict(
                    axis=dict(range=[0, 100]),
                    bar=dict(color=sev_clr),
                    steps=[
                        dict(range=[0, 40], color="rgba(63,185,80,0.2)"),
                        dict(range=[40, 70], color="rgba(210,153,34,0.2)"),
                        dict(range=[70, 100], color="rgba(248,81,73,0.2)"),
                    ],
                ),
            )
        )
        fig.update_layout(
            paper_bgcolor="#0d1117", font_color="#c9d1d9",
            height=250, margin=dict(t=30, b=10, l=20, r=20),
        )
        st.plotly_chart(fig, width="stretch")

        # Threat intel lookup
        if src_ip:
            intel = check_ip(src_ip)
            if intel:
                st.warning(f"⚠️ Source IP **{src_ip}** is in the threat intelligence database! "
                           f"Threat Level: **{intel['threat_level']}** | Source: {intel['source']}")
            else:
                st.info(f"Source IP {src_ip} not found in threat intelligence database.")

        st.markdown("#### Feature Summary")
        st.json(features)
