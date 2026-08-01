"""
Purpose:
Database Connection Engine for Jarvis AI OS.

Responsibilities:
- PostgreSQL ThreadedConnectionPool for production
- Automatic local SQLite fallback when DATABASE_URL is empty or points to sqlite file
- Auto-commit/rollback context manager transaction handling
- Safe parameterized query adapter (%s for Postgres, ? for SQLite)
"""

import os
import sqlite3
import datetime
import re
from contextlib import contextmanager

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
IS_POSTGRES = DATABASE_URL.startswith("postgresql://") or DATABASE_URL.startswith("postgres://")

_pg_pool = None

if IS_POSTGRES:
    try:
        import psycopg2
        import psycopg2.extras
        from psycopg2.pool import ThreadedConnectionPool
        _pg_pool = ThreadedConnectionPool(1, 20, DATABASE_URL)
        USE_POSTGRES = True
    except Exception:
        USE_POSTGRES = False
else:
    USE_POSTGRES = False

# Vercel Functions have a read-only deployed filesystem.  Their only writable
# location is /tmp, which is intentionally ephemeral between invocations.
DB_PATH = (
    "/tmp/jarvis.db"
    if os.getenv("VERCEL")
    else os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis.db")
)

class CursorProxy:
    def __init__(self, cursor):
        self._cursor = cursor
        self._lastrowid = None

    def __getattr__(self, name):
        return getattr(self._cursor, name)

    @property
    def lastrowid(self):
        return self._lastrowid

    def execute(self, query, params=None):
        adapted_query = query.replace("?", "%s")
        lower_query = adapted_query.lower()
        
        if "insert or replace" in lower_query:
            if "preferences" in lower_query:
                adapted_query = re.sub(
                    r'insert\s+or\s+replace\s+into\s+preferences\s*\((.*?)\)\s*values\s*\((.*?)\)',
                    r'INSERT INTO preferences (\1) VALUES (\2) ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value',
                    adapted_query,
                    flags=re.IGNORECASE
                )
            elif "document_chunks" in lower_query:
                adapted_query = re.sub(
                    r'insert\s+or\s+replace\s+into\s+document_chunks',
                    r'INSERT INTO document_chunks',
                    adapted_query,
                    flags=re.IGNORECASE
                )
                if "on conflict" not in adapted_query.lower():
                    adapted_query += " ON CONFLICT (id) DO UPDATE SET source_file = EXCLUDED.source_file, page_number = EXCLUDED.page_number, chunk_index = EXCLUDED.chunk_index, content = EXCLUDED.content, metadata_json = EXCLUDED.metadata_json, created_at = EXCLUDED.created_at"

        is_insert = query.strip().lower().startswith("insert")
        if is_insert and "returning id" not in adapted_query.lower():
            clean_query = adapted_query.strip()
            if clean_query.endswith(";"):
                clean_query = clean_query[:-1].strip()
            adapted_query = f"{clean_query} RETURNING id"

        self._cursor.execute(adapted_query, params or ())
        
        if is_insert:
            try:
                row = self._cursor.fetchone()
                if row:
                    if isinstance(row, dict):
                        self._lastrowid = row.get("id")
                    elif isinstance(row, tuple) or isinstance(row, list):
                        self._lastrowid = row[0]
                    else:
                        self._lastrowid = getattr(row, "id", None)
            except Exception:
                self._lastrowid = None

    def executemany(self, query, seq_of_params):
        adapted_query = query.replace("?", "%s")
        return self._cursor.executemany(adapted_query, seq_of_params)


class ConnectionProxy:
    def __init__(self, conn):
        self._conn = conn

    def __getattr__(self, name):
        return getattr(self._conn, name)

    def execute(self, query, params=None):
        import psycopg2.extras
        adapted_query = query.replace("?", "%s")
        lower_query = adapted_query.lower()
        
        if "insert or replace" in lower_query:
            if "preferences" in lower_query:
                adapted_query = re.sub(
                    r'insert\s+or\s+replace\s+into\s+preferences\s*\((.*?)\)\s*values\s*\((.*?)\)',
                    r'INSERT INTO preferences (\1) VALUES (\2) ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value',
                    adapted_query,
                    flags=re.IGNORECASE
                )
            elif "document_chunks" in lower_query:
                adapted_query = re.sub(
                    r'insert\s+or\s+replace\s+into\s+document_chunks',
                    r'INSERT INTO document_chunks',
                    adapted_query,
                    flags=re.IGNORECASE
                )
                if "on conflict" not in adapted_query.lower():
                    adapted_query += " ON CONFLICT (id) DO UPDATE SET source_file = EXCLUDED.source_file, page_number = EXCLUDED.page_number, chunk_index = EXCLUDED.chunk_index, content = EXCLUDED.content, metadata_json = EXCLUDED.metadata_json, created_at = EXCLUDED.created_at"

        cursor = self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        is_insert = query.strip().lower().startswith("insert")
        if is_insert and "returning id" not in adapted_query.lower():
            clean_query = adapted_query.strip()
            if clean_query.endswith(";"):
                clean_query = clean_query[:-1].strip()
            adapted_query = f"{clean_query} RETURNING id"

        cursor.execute(adapted_query, params or ())
        
        proxy = CursorProxy(cursor)
        if is_insert:
            try:
                row = cursor.fetchone()
                if row:
                    if isinstance(row, dict):
                        proxy._lastrowid = row.get("id")
                    elif isinstance(row, tuple) or isinstance(row, list):
                        proxy._lastrowid = row[0]
                    else:
                        proxy._lastrowid = getattr(row, "id", None)
            except Exception:
                proxy._lastrowid = None
        return proxy

    def cursor(self):
        import psycopg2.extras
        cursor = self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        return CursorProxy(cursor)


@contextmanager
def get_connection():
    """Context manager for Database connection (supports PostgreSQL pool & SQLite auto-commit/rollback)."""
    if USE_POSTGRES and _pg_pool:
        conn = _pg_pool.getconn()
        try:
            yield ConnectionProxy(conn)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            _pg_pool.putconn(conn)
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

def adapt_query(query: str) -> str:
    """Adapts SQL query placeholders: %s for PostgreSQL, ? for SQLite."""
    if USE_POSTGRES:
        return query.replace("?", "%s")
    return query

def init_db():
    """Initializes schema for conversations, preferences, and document_chunks tables."""
    with get_connection() as conn:
        cursor = conn.cursor()
        if USE_POSTGRES:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id SERIAL PRIMARY KEY,
                    timestamp VARCHAR(64) NOT NULL,
                    user_message TEXT NOT NULL,
                    assistant_reply TEXT NOT NULL,
                    provider VARCHAR(64) NOT NULL
                );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON conversations(timestamp);")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS preferences (
                    id SERIAL PRIMARY KEY,
                    key VARCHAR(128) UNIQUE NOT NULL,
                    value TEXT NOT NULL
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id VARCHAR(128) PRIMARY KEY,
                    source_file VARCHAR(255) NOT NULL,
                    page_number INTEGER NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at VARCHAR(64) NOT NULL
                );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_source_file ON document_chunks(source_file);")
        else:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    assistant_reply TEXT NOT NULL,
                    provider TEXT NOT NULL
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON conversations(timestamp);")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id TEXT PRIMARY KEY,
                    source_file TEXT NOT NULL,
                    page_number INTEGER NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_source_file ON document_chunks(source_file);")

            default_prefs = {
                "language": "Hinglish",
                "user_name": "Boss",
                "assistant_name": "Jarvis",
                "provider": "Groq",
                "theme": "Dark"
            }
            for k, v in default_prefs.items():
                cursor.execute("INSERT OR IGNORE INTO preferences (key, value) VALUES (?, ?)", (k, v))

# Auto-initialize database schema on module import
init_db()

def log_conversation_turn(user_msg: str, assistant_reply: str, provider: str = "Groq", latency: float = 0.0):
    """Compatibility helper writing turn directly into conversations table via context manager."""
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with get_connection() as conn:
            cursor = conn.cursor()
            sql = adapt_query("INSERT INTO conversations (timestamp, user_message, assistant_reply, provider) VALUES (?, ?, ?, ?)")
            cursor.execute(sql, (timestamp, user_msg, assistant_reply, provider))
    except Exception as e:
        print(f"[Database Error] Failed to log turn: {e}")
