# Lab 12: Secrets in git history

An early commit added a fake `.env` with `AZURE_DEVOPS_PAT`. A later commit deleted the file from `HEAD`, but the value remains in history.

**OWASP Top 10:2025:** [A02 Security Misconfiguration](https://owasp.org/Top10/2025/) / [A04 Cryptographic Failures](https://owasp.org/Top10/2025/) (secret exposure)

**Code:** git history for `.env` (not present at `HEAD`); see also `.env.example`

## Exploit

From the repo root (`vulnerable-python`):

```bash
git log -p --all -S 'AZURE_DEVOPS_PAT' -- .env
```

Or shorter:

```bash
git log -S AZURE_DEVOPS_PAT
```

You should see the commit that introduced the fake PAT and the commit that removed `.env`. The secret is gone from the working tree but still recoverable from history.

## Fix

- Never commit secrets. Use `.env.example` with placeholders only; keep real values out of git.
- If a secret was committed: rotate it immediately, then purge history (e.g. `git filter-repo`) or treat the repo as compromised for that credential.
- Block accidental commits with pre-commit secret scanners and branch protection.

Deleting the file on `main` alone is not enough. History still holds the old blob.
