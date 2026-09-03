# ByteBazaar labs

Short exploit-and-fix notes for this intentionally vulnerable shop (inspired by [DVWA](https://github.com/digininja/DVWA)). Findings map to [OWASP Top 10:2025](https://owasp.org/Top10/2025/).

**Local use only.** Do not expose the stack to the internet.

Fuller instructor materials may live outside this public repo. In code, look for `VULN:` (broken on purpose) and `SAFE:` (how to fix).

## Quick start

```bash
docker compose up --build
```

App: http://localhost:8888

| Username | Password  | Role     |
|----------|-----------|----------|
| alice    | alice123  | customer |
| bob      | bob123    | customer |
| admin    | admin123  | admin    |

Bob's order is usually `/orders/1`. Test card: `4242 4242 4242 4242`.

## Labs

| # | File | Topic | OWASP 2025 |
|---|------|-------|------------|
| 01 | [01-bola-idor.md](01-bola-idor.md) | IDOR on orders | A01 Broken Access Control |
| 02 | [02-ssrf-imds.md](02-ssrf-imds.md) | SSRF to IMDS / Key Vault | A01 / A02 |
| 03 | [03-sqli.md](03-sqli.md) | SQL injection on search | A05 Injection |
| 03b | [03b-nosql.md](03b-nosql.md) | NoSQL injection on tags | A05 Injection |
| 04 | [04-mass-assignment.md](04-mass-assignment.md) | Register with `role=admin` | A06 Insecure Design |
| 05 | [05-xss-token-theft.md](05-xss-token-theft.md) | Stored XSS + token theft | A05 / A07 |
| 06 | [06-price-tamper-checkout.md](06-price-tamper-checkout.md) | Client `amount_cents` | A06 Insecure Design |
| 07 | [07-jwt-alg-none.md](07-jwt-alg-none.md) | JWT `alg=none` | A07 Authentication Failures |
| 08 | [08-crypto-pan-storage.md](08-crypto-pan-storage.md) | PAN/CVV at rest | A04 Cryptographic Failures |
| 09 | [09-misconfig-debug.md](09-misconfig-debug.md) | Debug + verbose SQL errors | A02 / A10 |
| 10 | [10-logging-failures.md](10-logging-failures.md) | Passwords/PAN in logs | A09 Logging Failures |
| 11 | [11-ppe-pipeline.md](11-ppe-pipeline.md) | Poisoned pipeline YAML | A03 / A08 |
| 12 | [12-secrets-in-git.md](12-secrets-in-git.md) | Secret in git history | A02 / A04 |
