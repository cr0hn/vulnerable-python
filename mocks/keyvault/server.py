"""
Local stand-in for Azure Key Vault secrets API.

Demonstrates least privilege: the over-privileged IMDS token can list/read
everything; the scoped token can only read `storefront-api-key`.
"""

from flask import Flask, jsonify, request

app = Flask(__name__)

SECRETS = {
    "storefront-api-key": "bbz_live_ok_to_leak_in_lab_only",
    "payment-signing-key": "PAY_SIGNING_KEY_DO_NOT_SHIP",
    "db-admin-password": "postgres-root-equivalent-lab-only",
    "ci-service-connection": "AZDO_PAT_lab_only_xxxxxxxx",
}

OVERPRIV = "imds-token-OVERPRIVILEGED-can-read-all-secrets"
SCOPED = "imds-token-SCOPED-only-storefront-key"


def _bearer():
    auth = request.headers.get("Authorization", "")
    if auth.lower().startswith("bearer "):
        return auth.split(" ", 1)[1].strip()
    return ""


@app.get("/secrets")
def list_secrets():
    token = _bearer()
    if token == OVERPRIV:
        return jsonify({"value": [{"id": f"/secrets/{k}"} for k in SECRETS]})
    if token == SCOPED:
        return jsonify({"value": [{"id": "/secrets/storefront-api-key"}]})
    return jsonify({"error": "unauthorized"}), 401


@app.get("/secrets/<name>")
def get_secret(name):
    token = _bearer()
    if name not in SECRETS:
        return jsonify({"error": "not found"}), 404
    if token == OVERPRIV:
        return jsonify({"value": SECRETS[name], "name": name})
    if token == SCOPED and name == "storefront-api-key":
        return jsonify({"value": SECRETS[name], "name": name})
    return jsonify({"error": "forbidden"}), 403


@app.get("/health")
def health():
    return {"ok": True}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8091)
