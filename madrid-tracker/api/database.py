"""
Database connection helper for Neon PostgreSQL.
Uses psycopg2 with a simple connection-per-request pattern suitable for
a low-traffic personal dashboard.
"""
import os
import psycopg2
import psycopg2.extras
from contextlib import contextmanager


def _get_connection():
    url = os.environ["DATABASE_URL"]
    return psycopg2.connect(url, cursor_factory=psycopg2.extras.RealDictCursor)


@contextmanager
def get_db():
    """Yield a database connection, committing on success or rolling back on error."""
    conn = _get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
