---
kind: external_dependency
name: Gmail SMTP Email Service
slug: gmail-smtp
category: external_dependency
category_hints:
    - auth_protocol
scope:
    - '**'
---

### Gmail SMTP Email Service
- **Role**: Outbound email alerts for critical/high severity threats sent to configured administrator recipients
- **Authentication**: Uses Gmail App Passwords (not regular passwords) stored in `settings` table; requires `smtp_email` and `smtp_password` configuration
- **Delivery**: Multi-recipient support via `email_recipients` table; only active recipients receive alerts
- **Protocol**: Standard SMTP over TLS (port 587); message includes threat details, incident ID, and recommended actions
- **Fallback**: Returns False silently if credentials missing or no recipients configured