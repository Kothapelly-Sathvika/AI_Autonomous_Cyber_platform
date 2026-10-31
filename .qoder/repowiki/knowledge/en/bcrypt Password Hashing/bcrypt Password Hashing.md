---
kind: external_dependency
name: bcrypt Password Hashing
slug: bcrypt
category: external_dependency
category_hints:
    - auth_protocol
scope:
    - '**'
---

### bcrypt Password Hashing
- **Role**: Secure password hashing for user authentication system
- **Integration**: Used in `auth/authentication.py` for password registration, login verification, and password reset functionality
- **Usage model**: All user passwords stored as bcrypt hashes in the `users` table; supports role-based access control (Admin/Analyst)
- **Security**: Industry-standard adaptive hashing algorithm resistant to brute-force attacks