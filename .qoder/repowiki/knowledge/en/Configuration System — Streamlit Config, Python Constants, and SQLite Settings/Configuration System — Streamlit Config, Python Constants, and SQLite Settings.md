---
kind: configuration_system
name: Configuration System — Streamlit Config, Python Constants, and SQLite Settings
category: configuration_system
scope:
    - '**'
source_files:
    - .streamlit/config.toml
    - utils/config.py
    - core/database.py
    - app.py
---

The platform uses a three-tier configuration approach that combines Streamlit's built-in config file, Python module-level constants, and runtime settings persisted in an SQLite database.

**1. Streamlit application config (`.streamlit/config.toml`)**
- Declares the dark theme colors, font, server mode (`headless = true`, `port = 8501`), and disables usage telemetry (`gatherUsageStats = false`).
- This is the only place Streamlit-specific runtime options are defined; `app.py` also calls `st.set_page_config()` for page title/icon/layout but does not read from this file directly.

**2. Python defaults and environment overrides (`utils/config.py`)**
- Defines base paths (`BASE_DIR`, `DATA_DIR`, `DB_PATH`, `LOG_PATH`) derived from the module location, with `DATA_DIR` created on import if missing.
- Holds static application constants: SMTP defaults (`smtp.gmail.com:587`), severity levels, attack types, and app metadata (`APP_TITLE`, `APP_ICON`, `APP_VERSION`).
- Reads exactly one environment variable at import time: `ADMIN_EMAIL` via `os.environ.get("ADMIN_EMAIL", "admin@example.com")`. No `.env` loading or dotenv parsing is performed despite `python-dotenv==1.0.0` being listed in `requirements.txt`.

**3. Runtime settings stored in SQLite (`core/database.py`)**
- On first run, `init_db()` seeds a `settings` table with default key/value pairs: `smtp_server`, `smtp_port`, `smtp_email`, `smtp_password`, `alarm_enabled`, `auto_block`, `auto_email`, `simulation_speed`.
- Provides `get_setting(key, default)` and `set_setting(key, value)` helpers used by the Settings UI to persist user changes across sessions.
- Additional runtime state tables include `users`, `incidents`, `blocked_ips`, `threat_intel`, `audit_log`, and `email_recipients`.

**4. App bootstrap (`app.py`)**
- Initializes the database and seeds the admin user before any UI renders.
- Uses `st.session_state` for per-session flags (`authenticated`, `user`, `active_sessions`) rather than persistent session storage.
- Routes authenticated users to feature modules via a sidebar radio selector; no configuration-driven routing is present.

**Conventions and constraints observed**
- Configuration is split by concern: deployment/server config lives in `.streamlit/config.toml`, code-level defaults live in `utils/config.py`, and user-editable runtime values live in the SQLite `settings` table.
- Environment variables are not loaded from a `.env` file; only `ADMIN_EMAIL` is read directly from the process environment.
- Path configuration is relative to the package location (`Path(__file__).parent.parent`), ensuring portability regardless of how the app is invoked.
- There is no schema validation, type coercion, or centralized config object — each module imports the constants it needs.