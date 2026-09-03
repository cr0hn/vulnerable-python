import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me-not-for-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://bytebazaar:bytebazaar@localhost:5432/bytebazaar",
    )
    MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017/bytebazaar")
    IMDS_URL = os.environ.get("IMDS_URL", "http://127.0.0.1:8090")
    KEYVAULT_URL = os.environ.get("KEYVAULT_URL", "http://127.0.0.1:8091")
    # VULN (A04 / A07): weak, hardcoded JWT HMAC secret. SAFE: strong secret from a vault, rotated.
    JWT_SECRET = os.environ.get("JWT_SECRET", "supersecret")
    # Accepted test card (Stripe-style). Any other PAN is declined by the simulator.
    TEST_CARD = "4242424242424242"
