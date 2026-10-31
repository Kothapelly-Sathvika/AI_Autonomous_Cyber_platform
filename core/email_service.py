"""
Email Alert Service – sends threat notifications via SMTP
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from core.database import get_setting, get_connection


def get_recipients():
    conn = get_connection()
    rows = conn.execute(
        "SELECT email FROM email_recipients WHERE is_active=1"
    ).fetchall()
    conn.close()
    return [r["email"] for r in rows]


def add_recipient(email: str):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO email_recipients (email) VALUES (?)", (email,)
        )
        conn.commit()
    finally:
        conn.close()


def remove_recipient(email: str):
    conn = get_connection()
    conn.execute("DELETE FROM email_recipients WHERE email=?", (email,))
    conn.commit()
    conn.close()


def send_verification_email(to_email: str, code: str, username: str) -> bool:
    """Send a 6-digit verification code to a newly registering user."""
    smtp_email = get_setting("smtp_email")
    smtp_password = get_setting("smtp_password")
    smtp_server = get_setting("smtp_server", "smtp.gmail.com")
    smtp_port = int(get_setting("smtp_port", "587"))

    if not smtp_email or not smtp_password:
        return False

    subject = "Your Cyber Defense Platform Verification Code"

    body = f"""
╔══════════════════════════════════════════════════╗
║   AUTONOMOUS AI CYBER DEFENSE PLATFORM          ║
║   Email Verification                            ║
╚══════════════════════════════════════════════════╝

Hello {username},

Thank you for registering on the AI Cyber Defense Platform.

Your verification code is:

    ┌─────────────────────┐
    │     {code}     │
    └─────────────────────┘

This code expires in 15 minutes.

If you did not create this account, please ignore this email.

— AI Cyber Defense Platform
"""

    msg = MIMEMultipart()
    msg["From"] = smtp_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_email, smtp_password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Verification email error: {e}")
        return False


def send_password_reset_email(to_email: str, new_password: str, username: str) -> bool:
    """Send a password-reset confirmation email."""
    smtp_email = get_setting("smtp_email")
    smtp_password = get_setting("smtp_password")
    smtp_server = get_setting("smtp_server", "smtp.gmail.com")
    smtp_port = int(get_setting("smtp_port", "587"))

    if not smtp_email or not smtp_password:
        return False

    subject = "Password Reset – Cyber Defense Platform"

    body = f"""
Hello {username},

Your password has been reset successfully.

New Password: {new_password}

Please log in and change your password immediately.

— AI Cyber Defense Platform
"""

    msg = MIMEMultipart()
    msg["From"] = smtp_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_email, smtp_password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Password reset email error: {e}")
        return False


def send_threat_alert(threat_info: dict) -> bool:
    """
    Send an email alert for a critical/high threat.
    Returns True on success, False on failure.
    """
    smtp_email = get_setting("smtp_email")
    smtp_password = get_setting("smtp_password")
    smtp_server = get_setting("smtp_server", "smtp.gmail.com")
    smtp_port = int(get_setting("smtp_port", "587"))

    if not smtp_email or not smtp_password:
        return False

    recipients = get_recipients()
    if not recipients:
        return False

    subject = f"🚨 Critical Cyber Threat Detected – {threat_info.get('incident_id', 'N/A')}"

    body = f"""
AUTONOMOUS AI CYBER DEFENSE PLATFORM – THREAT ALERT
════════════════════════════════════════════════════

Threat Type      : {threat_info.get('attack_type', 'Unknown')}
Severity         : {threat_info.get('severity', 'Unknown')}
Source IP        : {threat_info.get('source_ip', 'N/A')}
Destination IP   : {threat_info.get('dest_ip', 'N/A')}
Time             : {threat_info.get('timestamp', 'N/A')}
Confidence Score : {threat_info.get('confidence', 0):.1%}
Incident ID      : {threat_info.get('incident_id', 'N/A')}

Recommended Action:
  1. Block source IP immediately
  2. Isolate affected systems
  3. Review logs and forensic data
  4. Escalate to SOC Tier-2 if severity is Critical

This is an automated alert from the AI Cyber Defense Platform.
"""

    msg = MIMEMultipart()
    msg["From"] = smtp_email
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_email, smtp_password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Email send error: {e}")
        return False
