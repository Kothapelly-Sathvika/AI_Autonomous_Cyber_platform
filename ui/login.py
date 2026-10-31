"""
Login / Register / Verify / Forgot-password page
"""
import streamlit as st
from auth.authentication import (
    authenticate, register_user, user_exists, get_user_email,
    reset_user_password, verify_user, resend_code, get_pending_user_email,
)
from core.email_service import (
    send_verification_email, send_password_reset_email,
)
from core.database import get_setting


def _smtp_configured() -> bool:
    return bool(get_setting("smtp_email") and get_setting("smtp_password"))


def show_login():
    st.markdown(
        """
        <style>
        .login-container {
            max-width: 500px; margin: auto; padding: 2rem;
            background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
            border-radius: 16px; border: 1px solid #30363d;
            box-shadow: 0 0 30px rgba(0, 255, 200, 0.15);
        }
        .login-title {
            text-align: center; color: #58a6ff; font-size: 1.8rem;
            margin-bottom: 0.2rem;
        }
        .login-sub { text-align: center; color: #8b949e; margin-bottom: 1.5rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<p class="login-title">🛡️ Autonomous AI Cyber Defense</p>', unsafe_allow_html=True)
    st.markdown('<p class="login-sub">Secure Access Portal</p>', unsafe_allow_html=True)

    tab_login, tab_register, tab_verify, tab_forgot = st.tabs(
        ["Login", "Register", "Verify Email", "Forgot Password"]
    )

    # ── LOGIN ──────────────────────────────────────────────────
    with tab_login:
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="admin")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            remember = st.checkbox("Remember Me")
            submitted = st.form_submit_button("🔐 Login", width="stretch")

        if submitted:
            result = authenticate(username, password)
            if result and result.get("_pending_verification"):
                # User exists but not yet verified – redirect to Verify tab
                st.session_state["pending_verify_user"] = result["username"]
                st.warning("Your account is not yet verified. Please check your email and enter the code in the **Verify Email** tab.")
            elif result:
                st.session_state["authenticated"] = True
                st.session_state["user"] = result
                if remember:
                    st.session_state["remember_user"] = username
                st.rerun()
            else:
                st.error("Invalid username or password.")

    # ── REGISTER ───────────────────────────────────────────────
    with tab_register:
        if not _smtp_configured():
            st.warning(
                "⚠️ **SMTP not configured.** Ask the admin to set up email credentials in "
                "**Settings → Email** before registering. Without SMTP, the verification code "
                "cannot be sent to your email."
            )

        with st.form("register_form"):
            new_user = st.text_input("Choose Username")
            new_email = st.text_input("Email Address")
            new_pass = st.text_input("Password", type="password")
            confirm_pass = st.text_input("Confirm Password", type="password")
            role = st.selectbox("Role", ["analyst", "admin"])
            reg_submit = st.form_submit_button("📝 Register", width="stretch")

        if reg_submit:
            if not new_user or not new_pass or not new_email:
                st.warning("All fields are required.")
            elif new_pass != confirm_pass:
                st.error("Passwords do not match.")
            elif len(new_pass) < 6:
                st.warning("Password must be at least 6 characters.")
            elif not _smtp_configured():
                st.error("Cannot send verification email. SMTP is not configured.")
            else:
                ok, msg, code = register_user(new_user, new_pass, new_email, role)
                if ok:
                    # Send the real email
                    sent = send_verification_email(new_email, code, new_user)
                    if sent:
                        st.success(f"✅ {msg} Check your inbox at **{new_email}**.")
                        st.session_state["pending_verify_user"] = new_user
                        st.info("Go to the **Verify Email** tab and enter the 6-digit code.")
                    else:
                        st.error("Failed to send verification email. Check SMTP settings.")
                else:
                    st.error(msg)

    # ── VERIFY EMAIL ──────────────────────────────────────────
    with tab_verify:
        st.markdown("Enter the 6-digit code sent to your email to activate your account.")

        pending = st.session_state.get("pending_verify_user", "")
        with st.form("verify_form"):
            v_user = st.text_input("Username", value=pending)
            v_code = st.text_input("Verification Code (6 digits)", max_chars=6, placeholder="123456")
            v_submit = st.form_submit_button("✅ Verify Account", width="stretch")

        if v_submit:
            if not v_user or not v_code:
                st.warning("Both fields are required.")
            elif verify_user(v_user, v_code):
                st.success("🎉 Account verified! You can now log in.")
                st.session_state.pop("pending_verify_user", None)
            else:
                st.error("Invalid or expired code. Please try again or request a new one.")

        st.markdown("---")
        st.markdown("Didn't receive the code?")
        resend_user = st.text_input("Username for resend", key="resend_user")
        if st.button("📧 Resend Code"):
            if not _smtp_configured():
                st.error("SMTP not configured – cannot resend.")
            elif not resend_user:
                st.warning("Enter your username.")
            else:
                email = get_pending_user_email(resend_user)
                if email:
                    new_code = resend_code(resend_user)
                    sent = send_verification_email(email, new_code, resend_user)
                    if sent:
                        st.success(f"New code sent to **{email}**.")
                    else:
                        st.error("Failed to send. Check SMTP settings.")
                else:
                    st.error("User not found or already verified.")

    # ── FORGOT PASSWORD ────────────────────────────────────────
    with tab_forgot:
        with st.form("forgot_form"):
            fp_user = st.text_input("Username")
            fp_new = st.text_input("New Password", type="password")
            fp_submit = st.form_submit_button("🔄 Reset Password", width="stretch")

        if fp_submit:
            if not fp_user or not fp_new:
                st.warning("Both fields are required.")
            elif user_exists(fp_user):
                reset_user_password(fp_user, fp_new)
                # Try to send email notification
                user_email = get_user_email(fp_user)
                if user_email and _smtp_configured():
                    send_password_reset_email(user_email, fp_new, fp_user)
                    st.success(f"Password reset! A confirmation was sent to **{user_email}**.")
                else:
                    st.success("Password has been reset. Please login with the new password.")
            else:
                st.error("Username not found.")

    st.markdown("</div>", unsafe_allow_html=True)

    # Hint
    st.markdown(
        '<p style="text-align:center;color:#8b949e;font-size:0.85rem;margin-top:1rem;">'
        "Default admin: <b>admin</b> / <b>admin123</b></p>",
        unsafe_allow_html=True,
    )
