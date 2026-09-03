"""Orders (BOLA) and checkout (price tamper + card storage)."""

from flask import (
    Blueprint,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from authutil import login_required
from models import Order, OrderItem, PaymentAttempt, Product

bp = Blueprint("orders", __name__)


@bp.get("/orders")
@login_required
def my_orders():
    orders = g.db.scalars(
        select(Order)
        .where(Order.user_id == g.user.id)
        .options(selectinload(Order.items))
        .order_by(Order.id.desc())
    ).all()
    return render_template("shop/orders.html", orders=orders)


@bp.get("/orders/<int:order_id>")
@login_required
def order_detail(order_id):
    """
    VULN (A01 BOLA/IDOR): loads order by id after confirming the user is logged in,
    but never checks that order.user_id == current user.
    As alice, open /orders/1 (Bob's order).

    SAFE:
        order = g.db.get(Order, order_id)
        if not order or order.user_id != g.user.id:
            abort(404)  # or 403
    """
    order = g.db.scalar(
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.items).selectinload(OrderItem.product))
    )
    if not order:
        return render_template("shop/not_found.html"), 404
    # Role check only — identity, not ownership. Classic BOLA.
    if g.user.role not in ("customer", "admin"):
        flash("Forbidden.", "err")
        return redirect(url_for("shop.home"))
    return render_template("shop/order_detail.html", order=order)


@bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    cart = session.get("cart", {})
    if not cart:
        flash("Your cart is empty.", "err")
        return redirect(url_for("shop.cart_view"))

    items = []
    catalog_total = 0
    for pid, qty in cart.items():
        product = g.db.get(Product, int(pid))
        if product:
            line = product.price_cents * qty
            catalog_total += line
            items.append({"product": product, "qty": qty, "line_cents": line})

    if request.method == "GET":
        return render_template(
            "shop/checkout.html",
            items=items,
            total_cents=catalog_total,
            test_card="4242 4242 4242 4242",
        )

    # --- POST: place order ---
    shipping_name = request.form.get("shipping_name", g.user.display_name)
    shipping_address = request.form.get("shipping_address", "")
    pan = (request.form.get("card_number") or "").replace(" ", "").replace("-", "")
    cvv = request.form.get("card_cvv", "")
    # VULN (A06 Insecure Design / price tampering): trust amount from the client.
    # SAFE: recompute total server-side from cart + catalog prices only.
    try:
        charged = int(request.form.get("amount_cents") or catalog_total)
    except ValueError:
        charged = catalog_total

    accepted = pan == current_app.config["TEST_CARD"]
    # VULN (A10): on weird input, "fail open" and accept the payment anyway.
    # SAFE: fail closed; decline when validation cannot complete.
    if request.form.get("force_accept") == "1":
        accepted = True

    attempt = PaymentAttempt(
        user_id=g.user.id,
        pan=pan,
        cvv=cvv,
        amount_cents=charged,
        accepted=accepted,
    )
    g.db.add(attempt)

    if not accepted:
        g.db.commit()
        flash("Card declined. Use the test card 4242 4242 4242 4242.", "err")
        return render_template(
            "shop/checkout.html",
            items=items,
            total_cents=catalog_total,
            test_card="4242 4242 4242 4242",
        )

    order = Order(
        user_id=g.user.id,
        total_cents=charged,
        status="paid",
        shipping_name=shipping_name,
        shipping_address=shipping_address,
        card_last4=pan[-4:] if len(pan) >= 4 else "",
        card_pan_lab_only=pan,
    )
    g.db.add(order)
    g.db.flush()
    for row in items:
        g.db.add(
            OrderItem(
                order_id=order.id,
                product_id=row["product"].id,
                quantity=row["qty"],
                unit_price_cents=row["product"].price_cents,
            )
        )
    # VULN (A09): payment log includes PAN/CVV.
    print(f"[payment] user={g.user.id} pan={pan} cvv={cvv} amount={charged} OK")
    g.db.commit()
    session["cart"] = {}
    flash("Order placed. Thanks for shopping at ByteBazaar!", "ok")
    return redirect(url_for("orders.order_detail", order_id=order.id))
