"""
Admin Panel – user management, IP control, audit logs
"""
import streamlit as st
import pandas as pd
from auth.authentication import get_all_users, delete_user, reset_user_password, register_user, verify_user
from core.database import (
    get_blocked_ips_df, block_ip, unblock_ip, get_audit_df, get_connection, log_audit,
)


def show_admin():
    user = st.session_state.get("user", {})
    if user.get("role") != "admin":
        st.warning("⚠️ Admin access required.")
        return

    st.markdown("## ⚙️ Admin Panel")
    st.markdown("---")

    tab_users, tab_ips, tab_logs = st.tabs(["👤 Users", "🚫 Blocked IPs", "📋 Audit Log"])

    # ── USER MANAGEMENT ────────────────────────────────────────
    with tab_users:
        st.markdown("### Add New User")
        with st.form("admin_add_user"):
            c1, c2, c3, c4 = st.columns(4)
            new_user = c1.text_input("Username")
            new_email = c2.text_input("Email")
            new_pass = c3.text_input("Password", type="password")
            new_role = c4.selectbox("Role", ["analyst", "admin"])
            if st.form_submit_button("➕ Add User"):
                if new_user and new_pass and new_email:
                    ok, msg, _code = register_user(new_user, new_pass, new_email, new_role)
                    if ok:
                        # Admin-created users are auto-verified
                        verify_user(new_user, _code)
                        st.success("User created and verified!")
                    else:
                        st.error(msg)
                else:
                    st.warning("All fields required.")

        st.markdown("---")
        st.markdown("### Existing Users")
        users = get_all_users()
        if users:
            df_users = pd.DataFrame(users)
            st.dataframe(df_users, width="stretch", hide_index=True)

            st.markdown("---")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### Delete (Deactivate) User")
                del_user = st.selectbox("Select user", [u["username"] for u in users])
                if st.button("🗑️ Deactivate"):
                    u = next((u for u in users if u["username"] == del_user), None)
                    if u:
                        delete_user(u["id"])
                        log_audit(st.session_state["user"]["username"], "delete_user", del_user)
                        st.success(f"User {del_user} deactivated.")
                        st.rerun()

            with c2:
                st.markdown("#### Reset Password")
                rp_user = st.selectbox("Select user", [u["username"] for u in users], key="rp")
                rp_pass = st.text_input("New Password", type="password")
                if st.button("🔄 Reset"):
                    if rp_pass:
                        reset_user_password(rp_user, rp_pass)
                        st.success(f"Password reset for {rp_user}.")

    # ── BLOCKED IPS ────────────────────────────────────────────
    with tab_ips:
        st.markdown("### Block an IP")
        with st.form("block_ip_form"):
            c1, c2 = st.columns(2)
            ip_to_block = c1.text_input("IP Address")
            block_reason = c2.text_input("Reason")
            if st.form_submit_button("🚫 Block IP"):
                if ip_to_block:
                    block_ip(ip_to_block, block_reason, st.session_state["user"]["username"])
                    log_audit(st.session_state["user"]["username"], "block_ip", ip_to_block)
                    st.success(f"IP {ip_to_block} blocked.")
                    st.rerun()

        st.markdown("---")
        st.markdown("### Currently Blocked IPs")
        blocked_df = get_blocked_ips_df()
        if blocked_df.empty:
            st.info("No blocked IPs.")
        else:
            st.dataframe(blocked_df, width="stretch", hide_index=True)
            ip_to_unblock = st.selectbox("Select IP to unblock", blocked_df["ip"].tolist())
            if st.button("✅ Unblock"):
                unblock_ip(ip_to_unblock)
                log_audit(st.session_state["user"]["username"], "unblock_ip", ip_to_unblock)
                st.success(f"IP {ip_to_unblock} unblocked.")
                st.rerun()

    # ── AUDIT LOG ──────────────────────────────────────────────
    with tab_logs:
        st.markdown("### System Audit Log")
        audit_df = get_audit_df(500)
        if audit_df.empty:
            st.info("No audit entries.")
        else:
            st.dataframe(audit_df, width="stretch", hide_index=True, height=400)
            csv = audit_df.to_csv(index=False)
            st.download_button("📥 Download Audit Log", csv, "audit_log.csv", "text/csv")
