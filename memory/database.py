"""
Purpose:
Database Connection Engine for Jarvis AI OS.

Responsibilities:
- Support PostgreSQL connection pooling when DATABASE_URL is set
- Automatic local SQLite fallback when DATABASE_URL is empty or points to sqlite file
- Auto-commit/rollback context manager transaction handling
"""

import os
import sqlite3
import datetime
from contextlib import contextmanager

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
IS_POSTGRES = DATABASE_URL.startswith("postgresql://") or DATABASE_URL.startswith("postgres://")

# Try importing psycopg2 for PostgreSQL production connections
if IS_POSTGRES:
    try:
        import psycopg2
        import psycopg2.extras
        USE_POSTGRES = True
    except ImportError:
        USE_POSTGRES = False
else:
    USE_POSTGRES = False

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis.db")

@contextmanager
def get_connection():
    """Context manager for Database connection (supports PostgreSQL & SQLite auto-commit/rollback)."""
    if USE_POSTGRES:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.DictCursor)
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

def init_db():
    """Initializes schema for conversations, preferences, and document_chunks tables."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Conversations Table
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
            if USE_POSTGRES:
                cursor.execute(
                    "INSERT INTO conversations (timestamp, user_message, assistant_reply, provider) VALUES (%s, %s, %s, %s)",
                    (timestamp, user_msg, assistant_reply, provider)
                )
            else:
                cursor.execute(
                    "INSERT INTO conversations (timestamp, user_message, assistant_reply, provider) VALUES (?, ?, ?, ?)",
                    (timestamp, user_msg, assistant_reply, provider)
                )
    except Exception as e:
        print(f"[Database Error] Failed to log turn: {e}")
