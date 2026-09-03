"""Shared helpers. Prefer keeping vuln logic in the route files next to the bug."""

from functools import wraps

from flask import g, jsonify, redirect, request, session, url_for
import jwt
from flask import current_app


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("account.login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


def api_login_required(view):
    """
    Protect /api/v1/* with JWT from Authorization: Bearer.

    VULN (A07): accepts alg=none and trusts HS256 with a weak shared secret.
    SAFE: allowlist algorithms=["HS256"] (or RS256 + JWKS), verify exp/aud/iss,
    reject tokens with alg none, use a strong secret from a vault.
    """

    @wraps(view)
    def wrapped(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.lower().startswith("bearer "):
            return jsonify({"error": "missing bearer token"}), 401
        token = header.split(" ", 1)[1].strip()
        try:
            # VULN: algorithms not restricted; PyJWT can be tricked with alg=none
            # when verify_signature is effectively skipped for that alg.
            header_unverified = jwt.get_unverified_header(token)
            alg = header_unverified.get("alg", "HS256")
            if alg == "none":
                # VULN: forge tokens with {"alg":"none"} and an empty signature.
                payload = jwt.decode(token, options={"verify_signature": False})
            else:
                payload = jwt.decode(
                    token,
                    current_app.config["JWT_SECRET"],
                    algorithms=["HS256", "none"],
                )
        except Exception as exc:
            return jsonify({"error": f"invalid token: {exc}"}), 401
        g.api_user_id = int(payload.get("sub", 0))
        g.api_role = payload.get("role", "customer")
        return view(*args, **kwargs)

    return wrapped


def issue_api_token(user):
    """Issue a lab JWT. Students will forge a better one in the JWT lab."""
    return jwt.encode(
        {"sub": str(user.id), "role": user.role, "name": user.username},
        current_app.config["JWT_SECRET"],
        algorithm="HS256",
    )
