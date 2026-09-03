"""SSRF link-preview feature."""

import requests
from flask import Blueprint, current_app, flash, render_template, request

from authutil import login_required

bp = Blueprint("tools", __name__, url_prefix="/tools")


@bp.route("/preview", methods=["GET", "POST"])
@login_required
def preview():
    """
    "Link preview" for sharing product inspiration.

    VULN (A01 SSRF): server fetches any URL the user supplies, including hosts on
    the Docker network such as http://imds:8090/metadata/identity/oauth2/token
    Then reuse the token against http://keyvault:8091/secrets

    SAFE: allowlist schemes+hosts; block link-local / private ranges; never fetch
    IMDS or internal hostnames; use a locked-down egress proxy.
    """
    result = None
    url = ""
    if request.method == "POST":
        url = (request.form.get("url") or "").strip()
        try:
            # VULN: no allowlist, no block of private IPs, follows redirects.
            resp = requests.get(url, timeout=5, allow_redirects=True)
            result = {
                "status": resp.status_code,
                "headers": dict(resp.headers),
                "body": resp.text[:4000],
            }
        except Exception as exc:
            # VULN (A10): verbose error to the user.
            flash(f"Preview failed: {exc}", "err")
    return render_template(
        "shop/preview.html",
        url=url,
        result=result,
        hint_imds=f"{current_app.config['IMDS_URL']}/metadata/identity/oauth2/token",
        hint_kv=f"{current_app.config['KEYVAULT_URL']}/secrets",
    )
