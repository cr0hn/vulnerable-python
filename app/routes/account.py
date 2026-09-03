"""Login, register (mass assignment), profile, API token minting."""

from flask import (
    Blueprint,
    flash,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from sqlalchemy import select
from werkzeug.security import check_password_hash, generate_password_hash

from authutil import issue_api_token, login_required
from models import User

bp = Blueprint("account", __name__, url_prefix="/account")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = g.db.scalar(select(User).where(User.username == username))
        # VULN (A09): log credentials-adjacent detail; no lockout / no alert on spray.
        # SAFE: log user id + outcome only; alert on repeated failures; never log password.
        print(f"[login] user={username!r} password={password!r} ok={bool(user)}")
        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            # VULN (A05 XSS chain): also stash a JWT-like session hint in a
            # template that writes it to localStorage (see base layout).
            # SAFE: httpOnly Secure cookie session only; no tokens in JS-readable storage.
            session["js_token"] = issue_api_token(user)
            flash(f"Welcome back, {user.display_name or user.username}.", "ok")
            return redirect(request.args.get("next") or url_for("shop.home"))
        # VULN (A09): fail quietly with no security alert channel.
        flash("Invalid username or password.", "err")
    return render_template("account/login.html")


@bp.post("/logout")
def logout():
    session.clear()
    flash("Signed out.", "ok")
    return redirect(url_for("shop.home"))


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Accept form OR JSON so Postman/Caido can send role easily.
        data = request.get_json(silent=True) or request.form.to_dict()
        email = (data.get("email") or "").strip()
        username = (data.get("username") or "").strip()
        password = data.get("password") or ""
        display_name = data.get("display_name") or username

        if not email or not username or not password:
            flash("Email, username, and password are required.", "err")
            return render_template("account/register.html")

        user = User(
            email=email,
            username=username,
            password_hash=generate_password_hash(password),
            display_name=display_name,
        )

        # VULN (A06 Mass assignment): copy every remaining key from the client onto
        # the User model, including `role`.
        # Try JSON: {"email":"...","username":"...","password":"...","role":"admin"}
        # SAFE: allowlist fields (email, username, password, display_name only).
        for key, value in data.items():
            if key in ("email", "username", "password", "display_name", "password_hash"):
                continue
            if hasattr(user, key):
                setattr(user, key, value)

        g.db.add(user)
        try:
            g.db.commit()
        except Exception:
            g.db.rollback()
            flash("Could not register (username or email taken?).", "err")
            return render_template("account/register.html")

        session["user_id"] = user.id
        session["js_token"] = issue_api_token(user)
        flash("Account created.", "ok")
        if request.is_json:
            return jsonify(
                {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role,
                    "api_token": issue_api_token(user),
                }
            )
        return redirect(url_for("shop.home"))
    return render_template("account/register.html")


@bp.get("/me")
@login_required
def me():
    token = issue_api_token(g.user)
    return render_template("account/me.html", api_token=token)


@bp.post("/profile")
@login_required
def update_profile():
    data = request.get_json(silent=True) or request.form.to_dict()
    # VULN (A06): same mass-assignment pattern on profile update.
    for key, value in data.items():
        if key in ("id", "password_hash"):
            continue
        if key == "password" and value:
            g.user.password_hash = generate_password_hash(value)
            continue
        if hasattr(g.user, key):
            setattr(g.user, key, value)
    g.db.commit()
    flash("Profile updated.", "ok")
    if request.is_json:
        return jsonify({"id": g.user.id, "role": g.user.role, "username": g.user.username})
    return redirect(url_for("account.me"))
