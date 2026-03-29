"""Optional compatibility wrapper for database access."""

from app.core.database import get_database, mongo_database

__all__ = ["get_database", "mongo_database"]
