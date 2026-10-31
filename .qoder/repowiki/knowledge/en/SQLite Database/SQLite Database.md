---
kind: external_dependency
name: SQLite Database
slug: sqlite
category: external_dependency
category_hints:
    - sdk_real_api
scope:
    - '**'
---

### SQLite Database
- **Role**: Local file-based persistence for users, incidents, blocked IPs, threat intelligence, audit logs, settings, and email recipients
- **Usage model**: Single database file at `data/cyberdefense.db`; connections use `check_same_thread=False` for multi-threaded access; `sqlite3.Row` row factory enables dict-like column access
- **Schema**: Six core tables — `users`, `incidents`, `blocked_ips`, `threat_intel`, `audit_log`, `settings`, plus `email_recipients` for alert distribution