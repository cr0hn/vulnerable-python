# Lab 08: PAN and CVV stored at rest

Checkout persists full PAN and CVV in `payment_attempts`, and full PAN again on `orders.card_pan_lab_only`.

**OWASP Top 10:2025:** [A04 Cryptographic Failures](https://owasp.org/Top10/2025/)

**Code:** `app/routes/orders.py` (`checkout`); `app/models.py` (`PaymentAttempt`, `Order.card_pan_lab_only`)

## Exploit

1. Sign in, add an item, checkout with card `4242 4242 4242 4242` and CVV `123`.
2. Inspect the database:

```bash
docker compose exec db psql -U bytebazaar -d bytebazaar -c \
  "SELECT id, user_id, pan, cvv, amount_cents, accepted FROM payment_attempts ORDER BY id DESC LIMIT 5;"
```

```bash
docker compose exec db psql -U bytebazaar -d bytebazaar -c \
  "SELECT id, user_id, card_last4, card_pan_lab_only, shipping_name FROM orders ORDER BY id;"
```

Bob's seeded order (usually id `1`) already has `card_pan_lab_only=4242424242424242`. Combined with lab 01, another user can already see order metadata via BOLA.

## Fix

- Never store PAN/CVV. Use a PSP tokenizer; keep only last4 + brand + processor reference.
- CVV must not remain at rest after authorization (PCI DSS).
- Masking in the UI while keeping plaintext columns is not enough.

Read `SAFE:` comments on the model fields and checkout handler.
