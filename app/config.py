"""Application configuration, read from environment variables."""
import os

# SQLite by default. Override with e.g. DATABASE_URL=sqlite:///./other.db
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./products.db")
