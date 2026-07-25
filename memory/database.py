import os
import sqlite3
import datetime
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis.db")

@contextmanager
def get_connection():
    """Context manager for SQLite database connection (auto commit/rollback & close)."""
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
    """Initializes schema for conversations and preferences tables."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Conversations Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_message TEXT NOT NULL,
                assistant_reply TEXT NOT NULL,
                provider TEXT NOT NULL
            )
        """)
        
        # 2. Preferences Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL
            )
        """)
        
        # Seed default preferences
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
    """Compatibility helper writing turn directly into SQLite conversations table via context manager."""
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO conversations (timestamp, user_message, assistant_reply, provider) VALUES (?, ?, ?, ?)",
                (timestamp, user_msg, assistant_reply, provider)
            )
    except Exception as e:
        print(f"[Database Error] Failed to log turn: {e}")
