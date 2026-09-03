# Lab 09: Debug mode and verbose errors

Compose ships with `FLASK_DEBUG=1`. Broken SQL can return driver exceptions to the browser.

**OWASP Top 10:2025:** [A02 Security Misconfiguration](https://owasp.org/Top10/2025/) / [A10 Mishandling of Exceptional Conditions](https://owasp.org/Top10/2025/)

**Code:** `docker-compose.yml` (`FLASK_DEBUG`); `app/factory.py`; `app/routes/shop.py` (search errors)

## Exploit

1. Confirm debug is on:

```bash
docker compose exec web printenv FLASK_DEBUG
```

Expect `1`.

2. Trigger a SQL error:

```text
http://localhost:8888/search?q=%27
```

3. The page shows a Postgres/SQLAlchemy error string (syntax error near …), not a generic failure. Attackers learn query shape and driver details.

Optional: checkout with `force_accept=1` in the POST is a fail-open payment path (same theme as A10).

## Fix

- `FLASK_DEBUG=0` / `DEBUG=False` in every deployed environment; fail CI if debug is enabled.
- Generic error page to clients; structured logs server-side only.
- Fail closed on payment validation (remove `force_accept`).

See `SAFE:` comments in `factory.py` and `shop.py`.
