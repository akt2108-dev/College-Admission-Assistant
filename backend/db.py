import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
import os
import json
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))


# ─────────────────────────────────────────────
#  Connection pool (reuse connections across requests)
# ─────────────────────────────────────────────

_pool = None


def _get_db_config():
    config = {
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT", "5432"),
    }

    missing = [key.upper() for key, value in config.items() if not value]
    if missing:
        raise RuntimeError(
            "Missing database environment variables: "
            + ", ".join(missing)
            + ". Set them in Railway Variables or backend/.env."
        )

    sslmode = os.getenv("DB_SSLMODE", "").strip()
    if sslmode:
        config["sslmode"] = sslmode

    return config


def _get_pool():
    global _pool
    if _pool is None:
        _pool = pool.SimpleConnectionPool(
            minconn=1,
            maxconn=int(os.getenv("DB_MAX_CONNECTIONS", "10")),
            **_get_db_config(),
        )
    return _pool


def get_connection():
    """
    Get a connection from the pool.
    Caller MUST return it via return_connection() or use execute_query/execute_non_query.
    """
    return _get_pool().getconn()


def return_connection(conn):
    """Return a connection back to the pool."""
    _get_pool().putconn(conn)


def execute_query(query, params=None):
    """
    Execute a SELECT query and return results as list of dictionaries.
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()
            return results
    finally:
        return_connection(conn)


def execute_non_query(query, params=None):
    """
    Execute INSERT/UPDATE/DELETE queries.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            conn.commit()
    finally:
        return_connection(conn)


# ─────────────────────────────────────────────
#  Conversation memory (DB-backed)
# ─────────────────────────────────────────────

_ENSURE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS conversation_memory (
    user_id TEXT PRIMARY KEY,
    memory JSONB NOT NULL DEFAULT '{}',
    updated_at TIMESTAMP DEFAULT NOW()
);
"""

_table_ensured = False

def _ensure_memory_table():
    """Create the conversation_memory table if it doesn't exist (runs once)."""
    global _table_ensured
    if _table_ensured:
        return
    execute_non_query(_ENSURE_TABLE_SQL)
    _table_ensured = True


def load_memory(user_id: str, default_factory):
    """Load conversation memory for a user from the DB. Returns default if not found."""
    _ensure_memory_table()
    rows = execute_query(
        "SELECT memory FROM conversation_memory WHERE user_id = %s;",
        (user_id,),
    )
    if rows:
        return rows[0]["memory"]
    return default_factory()


def save_memory(user_id: str, memory: dict):
    """Upsert conversation memory for a user into the DB."""
    _ensure_memory_table()
    execute_non_query(
        """
        INSERT INTO conversation_memory (user_id, memory, updated_at)
        VALUES (%s, %s, NOW())
        ON CONFLICT (user_id)
        DO UPDATE SET memory = EXCLUDED.memory, updated_at = NOW();
        """,
        (user_id, json.dumps(memory)),
    )


def delete_memory(user_id: str):
    """Delete conversation memory for a user."""
    _ensure_memory_table()
    execute_non_query(
        "DELETE FROM conversation_memory WHERE user_id = %s;",
        (user_id,),
    )
