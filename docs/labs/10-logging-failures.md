# Lab 10: Logging failures (passwords and PAN)

Login prints plaintext passwords. Successful payments print PAN and CVV to container stdout.

**OWASP Top 10:2025:** [A09 Security Logging and Alerting Failures](https://owasp.org/Top10/2025/)

**Code:** `app/routes/account.py` (login `print`); `app/routes/orders.py` (checkout `print`)

## Exploit

1. Log in as alice / alice123 (try a wrong password first if you want both outcomes).
2. Read logs:

```bash
docker compose logs web --tail=50
```

Look for lines like:

```text
[login] user='alice' password='alice123' ok=True
```

3. Complete a checkout with test card `4242 4242 4242 4242` and CVV `123`.
4. Check logs again for:

```text
[payment] user=… pan=4242424242424242 cvv=123 amount=… OK
```

Anyone with log access gets credentials and card data. There is no alert on repeated failures.

## Fix

Log outcome only - never password, PAN, CVV, or tokens:

```python
print(f"[login] user_id={user.id if user else None} ok={bool(ok)}")
```

Add alerts for repeated failures. Redact payment fields; log processor charge ids instead. See `SAFE:` comments in `account.py` and `orders.py`.
