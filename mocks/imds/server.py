"""
Local stand-in for Azure Instance Metadata Service (IMDS).

In Azure, http://169.254.169.254/metadata/identity/oauth2/token is only
reachable from the VM/container. Here the same idea is a service on the
Docker network named `imds`. An SSRF bug in the shop can reach it.
"""

from flask import Flask, jsonify, request

app = Flask(__name__)

# Tokens the Key Vault mock will accept. Two identities = least-privilege demo.
TOKENS = {
    "overprivileged": {
        "access_token": "imds-token-OVERPRIVILEGED-can-read-all-secrets",
        "expires_in": 3600,
        "resource": "https://vault.azure.net",
        "token_type": "Bearer",
        "client_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
    },
    "scoped": {
        "access_token": "imds-token-SCOPED-only-storefront-key",
        "expires_in": 3600,
        "resource": "https://vault.azure.net",
        "token_type": "Bearer",
        "client_id": "11111111-2222-3333-4444-555555555555",
    },
}


@app.get("/metadata/identity/oauth2/token")
def token():
    # Real IMDS requires Metadata: true. We accept it but do not enforce it,
    # so a naive SSRF still works (common teaching point).
    identity = request.args.get("client_id", "overprivileged")
    if identity not in TOKENS:
        # Default MI when client_id omitted: the over-privileged one.
        identity = "overprivileged"
    if request.args.get("client_id") == TOKENS["scoped"]["client_id"]:
        identity = "scoped"
    return jsonify(TOKENS[identity])


@app.get("/metadata/instance")
def instance():
    return jsonify(
        {
            "compute": {
                "name": "bytebazaar-web",
                "resourceGroupName": "rg-bytebazaar-lab",
                "subscriptionId": "00000000-0000-0000-0000-000000000000",
            }
        }
    )


@app.get("/health")
def health():
    return {"ok": True}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8090)
