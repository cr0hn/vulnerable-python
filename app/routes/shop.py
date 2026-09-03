"""Catalog, search (SQLi), cart, product detail + reviews (XSS), NoSQL tag filter."""

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
from sqlalchemy import select, text

from authutil import login_required
from models import Product, Review

bp = Blueprint("shop", __name__)


@bp.get("/")
def home():
    products = g.db.scalars(select(Product).order_by(Product.id)).all()
    return render_template("shop/home.html", products=products)


@bp.get("/products/<slug>")
def product_detail(slug):
    product = g.db.scalar(select(Product).where(Product.slug == slug))
    if not product:
        return render_template("shop/not_found.html"), 404
    reviews = g.db.scalars(
        select(Review).where(Review.product_id == product.id).order_by(Review.id.desc())
    ).all()
    return render_template("shop/product.html", product=product, reviews=reviews)


@bp.post("/products/<slug>/reviews")
@login_required
def add_review(slug):
    product = g.db.scalar(select(Product).where(Product.slug == slug))
    if not product:
        return render_template("shop/not_found.html"), 404
    body = request.form.get("body", "")
    rating = int(request.form.get("rating", 5) or 5)
    # VULN (A05 Stored XSS): body stored raw and later rendered with |safe.
    # SAFE: escape on render (Jinja default), or sanitize allowed tags server-side.
    review = Review(
        product_id=product.id,
        user_id=g.user.id,
        rating=max(1, min(5, rating)),
        body=body,
    )
    g.db.add(review)
    g.db.commit()
    flash("Thanks for the review!", "ok")
    return redirect(url_for("shop.product_detail", slug=slug))


@bp.get("/search")
def search():
    """
    Product search.

    VULN (A05 SQL Injection): query string is concatenated into SQL.
    Try: ' OR '1'='1
    Or UNION to read users (see docs/exploits/03-sqli.md).

    SAFE: use the ORM / bound parameters, never f-strings or %% formatting
    with user input inside SQL text.
    """
    q = request.args.get("q", "")
    # Intentionally vulnerable:
    sql = text(
        f"SELECT id, slug, name, description, price_cents, image, category, stock "
        f"FROM products WHERE name ILIKE '%{q}%' OR description ILIKE '%{q}%' "
        f"ORDER BY id"
    )
    # VULN (A10): on bad SQL we may surface the driver error to the browser when
    # debug is on. SAFE: generic error page; log details server-side only.
    try:
        rows = g.db.execute(sql).mappings().all()
    except Exception as exc:
        if current_app.config.get("DEBUG"):
            return (
                render_template(
                    "shop/search.html",
                    q=q,
                    products=[],
                    error=str(exc),
                ),
                500,
            )
        raise
    products = [dict(r) for r in rows]
    return render_template("shop/search.html", q=q, products=products, error=None)


@bp.get("/tags")
def tags():
    """
    Filter catalog by tag stored in MongoDB.

    VULN (A05 NoSQL Injection): the `tag` query param is parsed with a dangerous
    pattern. Sending tag[$ne]=x or a JSON body-like query string can broaden the
    match to include internal products.

    SAFE: treat input as a plain string; never pass request.args into Mongo
    operators; validate against an allowlist.
    """
    # Students can send: /tags?tag[$ne]=noop  via Caido/Postman (not a browser form).
    # Flask parses that into request.args with a weird key, so we also accept `q` JSON.
    raw = request.args.get("q")
    tag = request.args.get("tag", "")
    query = {}
    if raw:
        # VULN: trust client JSON as a Mongo filter.
        import json

        try:
            query = json.loads(raw)
        except json.JSONDecodeError:
            query = {"tags": raw}
    elif tag:
        query = {"tags": tag}
    else:
        query = {}

    # Also accept operator-style keys for the classic teaching payload.
    for key in request.args:
        if key.startswith("tag["):
            # e.g. tag[$ne]=x  →  {"tags": {"$ne": "x"}}
            op = key[4:-1] if key.endswith("]") else "$eq"
            query = {"tags": {op: request.args.get(key)}}
            break

    docs = list(current_app.mongo.product_tags.find(query if query else {}))
    slugs = [d["slug"] for d in docs]
    products = []
    if slugs:
        products = g.db.scalars(select(Product).where(Product.slug.in_(slugs))).all()
    # Show Mongo hits even when there is no Postgres product (the internal prize).
    extras = [s for s in slugs if s not in {p.slug for p in products}]
    return render_template(
        "shop/tags.html",
        tag=tag or raw or "",
        products=products,
        extras=extras,
        query=query,
    )


@bp.post("/cart/add/<int:product_id>")
def cart_add(product_id):
    product = g.db.get(Product, product_id)
    if not product:
        return redirect(url_for("shop.home"))
    cart = session.get("cart", {})
    key = str(product_id)
    cart[key] = cart.get(key, 0) + 1
    session["cart"] = cart
    flash(f"Added {product.name} to cart.", "ok")
    return redirect(request.referrer or url_for("shop.home"))


@bp.get("/cart")
def cart_view():
    cart = session.get("cart", {})
    items = []
    total = 0
    for pid, qty in cart.items():
        product = g.db.get(Product, int(pid))
        if product:
            line = product.price_cents * qty
            total += line
            items.append({"product": product, "qty": qty, "line_cents": line})
    return render_template("shop/cart.html", items=items, total_cents=total)


@bp.post("/cart/clear")
def cart_clear():
    session["cart"] = {}
    flash("Cart cleared.", "ok")
    return redirect(url_for("shop.cart_view"))
