"""
Live Monitoring – real-time event stream with AI analysis
"""
import streamlit as st
import time
import pandas as pd
from datetime import datetime
from core.simulator import generate_event
from core.threat_detection import ThreatDetector
from core.database import insert_incident, block_ip, get_setting, log_audit
from core.alarm_service import play_alarm
from core.email_service import send_threat_alert

# Singleton detector (cached across reruns)
@st.cache_resource
def get_detector():
    return ThreatDetector()


def show_monitoring():
    st.markdown("## 📡 Live Network Monitoring")
    st.markdown("---")

    detector = get_detector()

    # Controls
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        auto_run = st.toggle("▶️ Auto Simulate", value=True)
    with col2:
        speed = st.slider("Events / cycle", 1, 20, 5)
    with col3:
        st.markdown("")
        if st.button("⚡ Generate Single Event"):
            _process_event(detector)

    st.markdown("---")

    # Live event log stored in session state
    if "live_events" not in st.session_state:
        st.session_state["live_events"] = []
    if "alarm_active" not in st.session_state:
        st.session_state["alarm_active"] = False

    if auto_run:
        for _ in range(speed):
            _process_event(detector)

    # Alarm banner
    if st.session_state.get("alarm_active"):
        st.markdown(
            """
            <div style="
                background:#f8514922; border:2px solid #f85149; border-radius:10px;
                padding:1rem; text-align:center; animation: blink 1s infinite;
            ">
                <h2 style="color:#f85149;margin:0">🚨 CYBER ATTACK DETECTED 🚨</h2>
                <p style="color:#ffa198">High/Critical threat — Immediate action required</p>
            </div>
            <style>
            @keyframes blink {
                0%,100% {opacity:1} 50% {opacity:0.5}
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        if st.button("🔇 Acknowledge & Mute Alarm"):
            st.session_state["alarm_active"] = False
            st.rerun()

    # Event table
    events = st.session_state.get("live_events", [])
    if events:
        df = pd.DataFrame(events[-100:][::-1])
        display_cols = [
            "timestamp", "incident_id", "event_type", "attack_type",
            "severity", "source_ip", "dest_ip", "confidence",
        ]
        available = [c for c in display_cols if c in df.columns]
        st.dataframe(df[available], width="stretch", hide_index=True, height=450)
    else:
        st.info("Waiting for events…")

    # Auto-refresh
    if auto_run:
        time.sleep(1.5)
        st.rerun()


def _process_event(detector):
    event = generate_event()
    result = detector.analyze(event["features"])

    event["severity"] = result["severity"]
    event["confidence"] = result["confidence"]
    event["ai_prediction"] = result["attack_type"]
    event["is_anomaly"] = result["is_anomaly"]

    response = "Monitored"
    if result["is_anomaly"]:
        response = f"Blocked {event['source_ip']}"
        if get_setting("auto_block", "1") == "1":
            block_ip(event["source_ip"], reason=result["attack_type"])

        # Persist
        try:
            insert_incident(
                event["incident_id"], result["attack_type"], result["severity"],
                event["source_ip"], event["dest_ip"], result["confidence"],
                event["description"], response, result["attack_type"],
            )
        except Exception:
            pass  # duplicate incident_id (rare)

        # Alarm for High/Critical
        if result["severity"] in ("High", "Critical"):
            if get_setting("alarm_enabled", "1") == "1":
                play_alarm()
                st.session_state["alarm_active"] = True

        # Email alert for any anomaly (Spam, Medium, High, Critical)
        if get_setting("auto_email", "1") == "1":
            send_threat_alert(event)

        log_audit("system", "threat_detected",
                  f"{result['attack_type']} | {result['severity']} | {event['source_ip']}")

    if "live_events" not in st.session_state:
        st.session_state["live_events"] = []
    st.session_state["live_events"].append(event)
    # Keep last 500
    if len(st.session_state["live_events"]) > 500:
        st.session_state["live_events"] = st.session_state["live_events"][-500:]
