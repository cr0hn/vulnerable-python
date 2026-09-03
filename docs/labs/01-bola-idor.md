# Lab 01: BOLA / IDOR on order detail

Any logged-in customer can open any order by numeric id; login is checked, ownership is not.

**OWASP Top 10:2025:** [A01 Broken Access Control](https://owasp.org/Top10/2025/)

**Code:** `app/routes/orders.py` (`order_detail`) - see `VULN:` / `SAFE:` comments

## Exploit

1. `docker compose up --build` → http://localhost:8888
2. Sign in as **alice** / **alice123**.
3. Open **Orders**. You only see Alice's own orders in the list.
4. Browse to Bob's order (usually id `1`):

```text
http://localhost:8888/orders/1
```

5. You get HTTP 200 with Bob's shipping data (`Bob Builder`, `42 Pipeline Road, Build City`).

## Fix

Require ownership (or a real admin check) before rendering. Prefer a scoped query:

```python
order = g.db.scalar(
    select(Order).where(Order.id == order_id, Order.user_id == g.user.id)
)
if not order:
    abort(404)
```

Read the `SAFE:` comments next to the vulnerable handler.
