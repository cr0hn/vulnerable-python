"""Seed users, products, sample orders, and Mongo tag documents."""

from pymongo import MongoClient
from sqlalchemy import select
from werkzeug.security import generate_password_hash

from models import Order, OrderItem, Product, Review, User


PRODUCTS = [
    {
        "slug": "null-pointer-tee",
        "name": "Null Pointer Exception Tee",
        "description": (
            "A midweight unisex tee for the crash you saw coming and shipped anyway. "
            "Soft 180 gsm cotton with a clean front print of the classic NPE stack frame, "
            "side-seamed for a modern fit. Pre-shrunk so the joke survives the wash. "
            "Available feel: slightly broken-in from day one. Pair it with jeans, joggers, "
            "or the hoodie you swore you would not buy this sprint."
        ),
        "price_cents": 2890,
        "image": "null-pointer-tee.jpg",
        "category": "apparel",
    },
    {
        "slug": "sudo-mug",
        "name": "sudo make me coffee",
        "description": (
            "Ceramic mug, 350 ml, dishwasher-safe glaze, and a handle big enough for "
            "hands that typed through an incident. The exterior print reads "
            "`sudo make me coffee` in a monospace that looks like your terminal at 07:12. "
            "Does not grant root on the espresso machine. Does improve morale on Monday "
            "standups. Microwave safe; ego not included."
        ),
        "price_cents": 1890,
        "image": "sudo-mug.jpg",
        "category": "drinkware",
    },
    {
        "slug": "git-commit-hoodie",
        "name": 'git commit -m "fix" Hoodie',
        "description": (
            "Heavyweight fleece hoodie (320 gsm) with a kangaroo pocket for snacks, "
            "dongles, and unresolved merge conflicts. Front: subtle ByteBazaar mark. "
            "Back: the infamous `git commit -m \"fix\"` in oversized type, because we "
            "have all been that commit. Soft brushed interior, ribbed cuffs, and a hood "
            "deep enough to hide from product when the build is red."
        ),
        "price_cents": 5490,
        "image": "git-commit-hoodie.jpg",
        "category": "apparel",
    },
    {
        "slug": "rubber-duck-debug",
        "name": "Senior Rubber Duck",
        "description": (
            "The classic debugging companion, promoted to Senior. Bath-safe vinyl, "
            "cheerful yellow, and a deadpan expression that somehow asks better "
            "questions than half the PR comments you have written. Place it on your "
            "desk, explain the bug out loud, and watch the fix appear mid-sentence. "
            "No batteries. No Slack. Excellent listener. Terrible at writing tickets."
        ),
        "price_cents": 1290,
        "image": "rubber-duck.jpg",
        "category": "desk",
    },
    {
        "slug": "binary-socks",
        "name": "01 Binary Socks",
        "description": (
            "One pair of crew socks knitted with a binary motif that looks sharp under "
            "a desk camera. Soft cotton blend, reinforced heel and toe for long on-call "
            "weeks. Left foot leans toward 0, right toward 1, or swap them and invent "
            "your own endianness debate. Gift-ready for the engineer who already owns "
            "too many cables and somehow zero matching socks."
        ),
        "price_cents": 1490,
        "image": "binary-socks.jpg",
        "category": "apparel",
    },
    {
        "slug": "stack-overflow-sticker",
        "name": "I Copy From Stack Overflow Sticker Pack",
        "description": (
            "Eight weatherproof vinyl stickers for laptops, water bottles, and the "
            "back of your company badge (we did not say that). Designs include classic "
            "dev memes, a tiny accepted-answer checkmark, and a tasteful confession "
            "about reading the docs second. Easy peel, residue-light adhesive. Laptop "
            "not included. Shame neither."
        ),
        "price_cents": 990,
        "image": "sticker-pack.jpg",
        "category": "stickers",
    },
    {
        "slug": "segfault-poster",
        "name": "Segmentation Fault Wall Poster",
        "description": (
            "A2 matte art print of a stylized memory dump that somehow looks good in "
            "a living room. Printed on 200 gsm stock with a soft-touch finish so it "
            "does not glare under office LEDs. Hang it where the whiteboard used to "
            "live, or gift it to the teammate who still debugs with print statements. "
            "Frame not included; vibes absolutely included."
        ),
        "price_cents": 2490,
        "image": "segfault-poster.jpg",
        "category": "prints",
    },
    {
        "slug": "kubernetes-pin",
        "name": "Helmsman Enamel Pin",
        "description": (
            "Hard enamel pin with a tiny ship's wheel for the cluster wrangler in your "
            "life. Gold-tone metal, rubber clutch backing, roughly 25 mm across so it "
            "sits nicely on a hoodie, tote, or conference lanyard. Ships with a small "
            "backing card that says you kept production afloat (this sprint). Collect "
            "them. Or lose them in a hoodie pocket forever. Both are valid."
        ),
        "price_cents": 1190,
        "image": "k8s-pin.jpg",
        "category": "accessories",
    },
]


def seed_postgres(session):
    # Always refresh catalog copy/images so local updates land without wiping volumes.
    by_slug = {
        p.slug: p for p in session.scalars(select(Product)).all()
    }
    for data in PRODUCTS:
        existing = by_slug.get(data["slug"])
        if existing:
            existing.name = data["name"]
            existing.description = data["description"]
            existing.price_cents = data["price_cents"]
            existing.image = data["image"]
            existing.category = data["category"]
        else:
            session.add(Product(**data))
    session.commit()

    existing_user = session.scalar(select(User).limit(1))
    if existing_user:
        print(f"Catalog refreshed ({len(PRODUCTS)} products). Users already seeded.")
        return

    alice = User(
        email="alice@example.com",
        username="alice",
        password_hash=generate_password_hash("alice123"),
        role="customer",
        display_name="Alice",
    )
    bob = User(
        email="bob@example.com",
        username="bob",
        password_hash=generate_password_hash("bob123"),
        role="customer",
        display_name="Bob",
    )
    admin = User(
        email="admin@example.com",
        username="admin",
        password_hash=generate_password_hash("admin123"),
        role="admin",
        display_name="Store Admin",
    )
    session.add_all([alice, bob, admin])
    session.flush()

    products = session.scalars(select(Product).order_by(Product.id)).all()

    bob_order = Order(
        user_id=bob.id,
        total_cents=products[0].price_cents + products[1].price_cents,
        status="paid",
        shipping_name="Bob Builder",
        shipping_address="42 Pipeline Road, Build City",
        card_last4="4242",
        card_pan_lab_only="4242424242424242",
    )
    session.add(bob_order)
    session.flush()
    session.add_all(
        [
            OrderItem(
                order_id=bob_order.id,
                product_id=products[0].id,
                quantity=1,
                unit_price_cents=products[0].price_cents,
            ),
            OrderItem(
                order_id=bob_order.id,
                product_id=products[1].id,
                quantity=1,
                unit_price_cents=products[1].price_cents,
            ),
        ]
    )

    alice_order = Order(
        user_id=alice.id,
        total_cents=products[3].price_cents,
        status="paid",
        shipping_name="Alice",
        shipping_address="1 Curious Lane",
        card_last4="4242",
        card_pan_lab_only="4242424242424242",
    )
    session.add(alice_order)
    session.flush()
    session.add(
        OrderItem(
            order_id=alice_order.id,
            product_id=products[3].id,
            quantity=1,
            unit_price_cents=products[3].price_cents,
        )
    )

    session.add(
        Review(
            product_id=products[0].id,
            user_id=bob.id,
            rating=5,
            body="Fits great. Soft cotton, print survived two washes so far. Wore it to a postmortem and nobody noticed the irony.",
        )
    )
    session.commit()
    print(f"Seeded Postgres: users alice/bob/admin, {len(products)} products, sample orders.")


def seed_mongo(mongo_url: str):
    client = MongoClient(mongo_url)
    db = client.get_default_database()
    tags = db["product_tags"]
    if tags.estimated_document_count() > 0:
        return
    docs = [
        {"slug": "null-pointer-tee", "tags": ["cotton", "tee", "error", "funny"]},
        {"slug": "sudo-mug", "tags": ["mug", "ceramic", "coffee", "cli"]},
        {"slug": "git-commit-hoodie", "tags": ["hoodie", "git", "warm"]},
        {"slug": "rubber-duck-debug", "tags": ["duck", "debug", "desk", "classic"]},
        {"slug": "binary-socks", "tags": ["socks", "binary", "apparel"]},
        {"slug": "stack-overflow-sticker", "tags": ["sticker", "vinyl", "meme"]},
        {"slug": "segfault-poster", "tags": ["poster", "print", "crash"]},
        {"slug": "kubernetes-pin", "tags": ["pin", "kubernetes", "enamel"]},
        {"slug": "internal-staff-hoodie", "tags": ["internal", "staff-only", "do-not-list"]},
    ]
    tags.insert_many(docs)
    print(f"Seeded Mongo: {len(docs)} product_tags documents.")
