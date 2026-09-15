import time

from flask import Flask, g, session
from pymongo import MongoClient
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker

from config import Config
from models import Base, User
from seed import seed_mongo, seed_postgres


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # VULN (A02): DEBUG can be left on via env. SAFE: DEBUG never true in deployed envs.
    app.config["DEBUG"] = str(__import__("os").environ.get("FLASK_DEBUG", "0")) in (
        "1",
        "true",
        "True",
    )

    engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"], pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    app.engine = engine
    app.SessionLocal = SessionLocal

    mongo = MongoClient(app.config["MONGO_URL"])
    app.mongo = mongo.get_default_database()

    @app.before_request
    def open_db():
        g.db: Session = SessionLocal()
        uid = session.get("user_id")
        g.user = g.db.get(User, uid) if uid else None

    @app.teardown_request
    def close_db(_exc=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    @app.context_processor
    def inject_globals():
        cart = session.get("cart", {})
        return {
            "current_user": g.get("user"),
            "cart_count": sum(cart.values()) if cart else 0,
        }

    from routes.shop import bp as shop_bp
    from routes.account import bp as account_bp
    from routes.orders import bp as orders_bp
    from routes.api_v1 import bp as api_bp
    from routes.tools import bp as tools_bp

    app.register_blueprint(shop_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(tools_bp)

    # Retry: right after container start, the container's own DNS/network can
    # take a moment even though the db container is already healthy.
    for attempt in range(10):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            break
        except OperationalError:
            if attempt == 9:
                raise
            time.sleep(1)

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as s:
        seed_postgres(s)
    seed_mongo(app.config["MONGO_URL"])

    return app
