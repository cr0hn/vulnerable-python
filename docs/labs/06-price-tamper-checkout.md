# Lab 06: Price tampering at checkout

Checkout trusts `amount_cents` from the client, so you can pay catalog prices with a 1-cent charge.

**OWASP Top 10:2025:** [A06 Insecure Design](https://owasp.org/Top10/2025/)

**Code:** `app/routes/orders.py` (`checkout`); `app/templates/shop/checkout.html`

## Exploit

1. Sign in as alice / alice123.
2. Add an expensive item to the cart. Open **Checkout**.
3. Change **Amount (cents)** to `1` (DevTools or a proxy).
4. Shipping fields any. Card:

```text
4242 4242 4242 4242
```

CVV any 3 digits (e.g. `123`). Submit **Pay now**.

5. Order is created with `total_cents=1` while line items still show catalog prices.

## Fix

Ignore client amounts. Recompute from server-side cart + catalog prices only:

```python
charged = catalog_total  # Product.price_cents * qty
# never: int(request.form.get("amount_cents"))
```

Hiding the field or locking it with JavaScript does not help. Read `SAFE:` comments in `orders.py`.
