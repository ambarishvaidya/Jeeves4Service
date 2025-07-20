"""Application configuration module."""
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/user_db")