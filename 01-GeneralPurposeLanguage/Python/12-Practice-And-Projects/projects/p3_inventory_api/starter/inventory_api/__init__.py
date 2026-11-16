"""Inventory REST API (FastAPI + sqlite3)."""
from .app import create_app

__all__ = ["create_app"]
