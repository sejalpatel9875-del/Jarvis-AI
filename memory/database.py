import os
import sqlite3
import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis.db")

def get_connection() -> sqlite3.Connection:
    """Returns an active SQLite database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes schema for conversations and preferences tables."""
    conn = get_connection()
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
        
    conn.commit()
    conn.close()

# Auto-initialize database schema on module import
init_db()

def log_conversation_turn(user_msg: str, assistant_reply: str, provider: str = "Groq", latency: float = 0.0):
    """Compatibility helper writing turn directly into SQLite conversations table without circular imports."""
    try:
        conn = get_connection()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            "INSERT INTO conversations (timestamp, user_message, assistant_reply, provider) VALUES (?, ?, ?, ?)",
            (timestamp, user_msg, assistant_reply, provider)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[Database Error] Failed to log turn: {e}")
