"""
Settings – configure email, alarm, simulation, and threat intel
"""
import streamlit as st
from core.database import get_setting, set_setting
from core.email_service import get_recipients, add_recipient, remove_recipient
from core.threat_intel import get_all_intel, add_intel


def show_settings():
    st.markdown("## ⚙️ Settings")
    st.markdown("---")

    tab_email, tab_alarm, tab_sim, tab_intel = st.tabs(
        ["📧 Email", "🔔 Alarm", "🎮 Simulation", "🧠 Threat Intel"]
    )

    # ── EMAIL SETTINGS ─────────────────────────────────────────
    with tab_email:
        st.markdown("### SMTP Configuration")
        st.info(
            "**Required for user registration & password reset.** "
            "Configure a Gmail account with an [App Password](https://myaccount.google.com/apppasswords) "
            "to enable email verification codes, threat alerts, and password reset notifications."
        )
        current_email = get_setting("smtp_email")
        if current_email:
            st.success(f"SMTP configured: **{current_email}**")
        else:
            st.warning("SMTP not configured - registration and email features are disabled.")

        with st.form("email_settings"):
            smtp_server = st.text_input("SMTP Server", value=get_setting("smtp_server", "smtp.gmail.com"))
            smtp_port = st.text_input("SMTP Port", value=get_setting("smtp_port", "587"))
            smtp_email = st.text_input("Sender Email", value=get_setting("smtp_email"))
            smtp_pass = st.text_input("App Password", type="password", value=get_setting("smtp_password"))
            auto_email = st.checkbox("Auto-send email on any threat detection (Spam, Malware, etc.)", value=get_setting("auto_email") == "1")

            if st.form_submit_button("💾 Save Email Settings"):
                set_setting("smtp_server", smtp_server)
                set_setting("smtp_port", smtp_port)
                set_setting("smtp_email", smtp_email)
                set_setting("smtp_password", smtp_pass)
                set_setting("auto_email", "1" if auto_email else "0")
                st.success("Email settings saved!")

        st.markdown("---")
        st.markdown("### Alert Recipients")
        recipients = get_recipients()
        if recipients:
            for r in recipients:
                c1, c2 = st.columns([3, 1])
                c1.write(r)
                if c2.button("❌ Remove", key=f"rm_{r}"):
                    remove_recipient(r)
                    st.rerun()
        else:
            st.info("No recipients configured.")

        new_recip = st.text_input("Add recipient email")
        if st.button("➕ Add Recipient"):
            if new_recip:
                add_recipient(new_recip)
                st.success(f"Added {new_recip}")
                st.rerun()

    # ── ALARM SETTINGS ─────────────────────────────────────────
    with tab_alarm:
        st.markdown("### Alarm Configuration")
        with st.form("alarm_settings"):
            alarm_on = st.checkbox("Enable alarm for High/Critical threats",
                                   value=get_setting("alarm_enabled") == "1")
            if st.form_submit_button("💾 Save"):
                set_setting("alarm_enabled", "1" if alarm_on else "0")
                st.success("Alarm settings saved!")

    # ── SIMULATION SETTINGS ────────────────────────────────────
    with tab_sim:
        st.markdown("### Simulation Controls")
        with st.form("sim_settings"):
            auto_block = st.checkbox("Auto-block malicious IPs",
                                     value=get_setting("auto_block") == "1")
            speed = st.slider("Default simulation speed (events/cycle)",
                              1, 20, int(get_setting("simulation_speed", "3")))
            if st.form_submit_button("💾 Save"):
                set_setting("auto_block", "1" if auto_block else "0")
                set_setting("simulation_speed", str(speed))
                st.success("Simulation settings saved!")

    # ── THREAT INTELLIGENCE ────────────────────────────────────
    with tab_intel:
        st.markdown("### Threat Intelligence Database")
        intel_df = get_all_intel()
        if not intel_df.empty:
            st.dataframe(intel_df, width="stretch", hide_index=True, height=300)

        st.markdown("---")
        st.markdown("### Add Indicator")
        with st.form("add_intel"):
            c1, c2, c3, c4 = st.columns(4)
            indicator = c1.text_input("Indicator (IP/domain/country)")
            ind_type = c2.selectbox("Type", ["ip", "domain", "country"])
            threat_level = c3.selectbox("Threat Level", ["Low", "Medium", "High", "Critical"])
            source = c4.text_input("Source")
            if st.form_submit_button("➕ Add"):
                if indicator:
                    add_intel(indicator, ind_type, threat_level, source or "manual")
                    st.success("Indicator added!")
                    st.rerun()
