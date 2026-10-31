"""
Authentication module – register, login, session management, email verification
"""
import random
import string
from datetime import datetime, timedelta

import bcrypt
import streamlit as st
from core.database import get_connection, log_audit


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def _generate_code() -> str:
    """Generate a 6-digit verification code."""
    return "".join(random.choices(string.digits, k=6))


# ── Registration (creates unverified account) ─────────────────
def register_user(username: str, password: str, email: str, role: str = "analyst"):
    """Create a user with is_verified=0 and return (success, msg, code)."""
    code = _generate_code()
    expiry = (datetime.now() + timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO users
               (username, password_hash, email, role, is_verified,
                verification_code, verification_expiry)
               VALUES (?,?,?,?,?,?,?)""",
            (username, hash_password(password), email, role, 0, code, expiry),
        )
        conn.commit()
        log_audit(username, "register", f"Pending verification – code sent to {email}")
        return True, "Verification code sent to your email!", code
    except Exception:
        return False, "Username already exists.", None
    finally:
        conn.close()


# ── Verify email code ─────────────────────────────────────────
def verify_user(username: str, code: str) -> bool:
    """Verify the 6-digit code and activate the user."""
    conn = get_connection()
    row = conn.execute(
        "SELECT verification_code, verification_expiry, is_verified FROM users WHERE username=?",
        (username,),
    ).fetchone()
    if not row:
        conn.close()
        return False
    if row["is_verified"]:
        conn.close()
        return True  # already verified
    if row["verification_code"] != code:
        conn.close()
        return False
    # Check expiry
    if row["verification_expiry"]:
        expiry = datetime.strptime(row["verification_expiry"], "%Y-%m-%d %H:%M:%S")
        if datetime.now() > expiry:
            conn.close()
            return False
    # Activate
    conn.execute(
        "UPDATE users SET is_verified=1, verification_code=NULL, verification_expiry=NULL WHERE username=?",
        (username,),
    )
    conn.commit()
    conn.close()
    log_audit(username, "email_verified", "Account verified via email code")
    return True


def resend_code(username: str) -> str | None:
    """Generate a fresh verification code and return it (caller sends email)."""
    code = _generate_code()
    expiry = (datetime.now() + timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    conn.execute(
        "UPDATE users SET verification_code=?, verification_expiry=? WHERE username=? AND is_verified=0",
        (code, expiry, username),
    )
    conn.commit()
    conn.close()
    return code


# ── Login (only verified users) ───────────────────────────────
def authenticate(username: str, password: str):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE username=? AND is_active=1", (username,)
    ).fetchone()
    conn.close()
    if row and check_password(password, row["password_hash"]):
        if not row["is_verified"]:
            log_audit(username, "login_blocked", "Account not yet verified")
            return {"_pending_verification": True, "username": username}
        log_audit(username, "login", "Successful login")
        return dict(row)
    if row:
        log_audit(username, "login_failed", "Invalid password")
    return None


def get_all_users():
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, username, email, role, created_at, is_active, is_verified FROM users ORDER BY id"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_user(user_id: int):
    conn = get_connection()
    conn.execute("UPDATE users SET is_active=0 WHERE id=?", (user_id,))
    conn.commit()
    conn.close()


def reset_user_password(username: str, new_password: str):
    conn = get_connection()
    conn.execute(
        "UPDATE users SET password_hash=? WHERE username=?",
        (hash_password(new_password), username),
    )
    conn.commit()
    conn.close()
    log_audit(username, "password_reset", "Password was reset")


def user_exists(username: str) -> bool:
    conn = get_connection()
    row = conn.execute("SELECT 1 FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    return row is not None


def get_user_email(username: str):
    conn = get_connection()
    row = conn.execute("SELECT email FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    return row["email"] if row else None


def get_pending_user_email(username: str) -> str | None:
    """Return email of an unverified user, or None."""
    conn = get_connection()
    row = conn.execute(
        "SELECT email FROM users WHERE username=? AND is_verified=0 AND is_active=1",
        (username,),
    ).fetchone()
    conn.close()
    return row["email"] if row else None


# ── Seed default admin (pre-verified) ────────────────────────
def seed_default_admin():
    conn = get_connection()
    row = conn.execute("SELECT id FROM users WHERE role='admin'").fetchone()
    if not row:
        conn.execute(
            """INSERT INTO users
               (username, password_hash, email, role, is_verified)
               VALUES (?,?,?,?,1)""",
            ("admin", hash_password("admin123"), "admin@cyberdefense.local", "admin"),
        )
    else:
        # Ensure admin is always active and verified
        conn.execute(
            "UPDATE users SET is_active=1, is_verified=1 WHERE role='admin'"
        )
    conn.commit()
    conn.close()
