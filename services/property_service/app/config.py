"""Application configuration module."""
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://python:python@localhost:5432/J4S.Property_Service")
