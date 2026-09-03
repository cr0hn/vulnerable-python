"""JWT-protected JSON API (separate from cookie session)."""

from flask import Blueprint, g, jsonify
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from authutil import api_login_required
from models import Order, OrderItem, User

bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")


@bp.get("/me")
@api_login_required
def me():
    user = g.db.get(User, g.api_user_id)
    if not user:
        return jsonify({"error": "user not found"}), 404
    return jsonify(
        {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "email": user.email,
        }
    )


@bp.get("/orders")
@api_login_required
def list_orders():
    # Admin role from a forged JWT sees everyone.
    q = select(Order).options(selectinload(Order.items))
    if g.api_role != "admin":
        q = q.where(Order.user_id == g.api_user_id)
    orders = g.db.scalars(q.order_by(Order.id.desc())).all()
    return jsonify(
        [
            {
                "id": o.id,
                "user_id": o.user_id,
                "total_cents": o.total_cents,
                "status": o.status,
                "shipping_name": o.shipping_name,
            }
            for o in orders
        ]
    )


@bp.get("/admin/users")
@api_login_required
def admin_users():
    """
    VULN (A07): authorization trusts the `role` claim inside the JWT.
    Forge alg=none token with role=admin → full user list (emails included).

    SAFE: look up role from the database (or IdP), never from client-controlled claims.
    """
    if g.api_role != "admin":
        return jsonify({"error": "admin only"}), 403
    users = g.db.scalars(select(User).order_by(User.id)).all()
    return jsonify(
        [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "role": u.role,
            }
            for u in users
        ]
    )
