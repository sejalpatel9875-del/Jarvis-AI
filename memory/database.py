import os
import sqlite3
import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis.db")

def get_connection():
    """Returns an active SQLite database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes SQLite schema for structured Jarvis memory."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Profile Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profile (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    
    # Default profile values
    defaults = {
        "assistant_name": "Jarvis",
        "user_name": "Boss",
        "preferred_language": "Hinglish (Hindi + English)",
        "city": "",
        "timezone": ""
    }
    for k, v in defaults.items():
        cursor.execute("INSERT OR IGNORE INTO profile (key, value) VALUES (?, ?)", (k, v))
        
    # 2. User Facts Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_facts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fact_key TEXT UNIQUE NOT NULL,
            fact_value TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 3. Custom Contacts Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS custom_contacts (
            name TEXT PRIMARY KEY,
            phone TEXT NOT NULL
        )
    """)
    
    # 4. Conversation History Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_msg TEXT NOT NULL,
            assistant_reply TEXT NOT NULL,
            provider TEXT,
            latency REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 5. Projects Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            name TEXT PRIMARY KEY,
            details TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

# Initialize DB on module import
init_db()

# DB Query Functions
def set_profile_value(key: str, value: str):
    conn = get_connection()
    conn.execute("INSERT OR REPLACE INTO profile (key, value) VALUES (?, ?)", (key.strip().lower(), value.strip()))
    conn.commit()
    conn.close()

def get_profile_value(key: str, default: str = "") -> str:
    conn = get_connection()
    row = conn.execute("SELECT value FROM profile WHERE key = ?", (key.strip().lower(),)).fetchone()
    conn.close()
    return row["value"] if row else default

def save_user_fact(key: str, value: str):
    conn = get_connection()
    conn.execute("INSERT OR REPLACE INTO user_facts (fact_key, fact_value) VALUES (?, ?)", (key.strip().lower(), value.strip()))
    conn.commit()
    conn.close()

def get_all_user_facts() -> dict:
    conn = get_connection()
    rows = conn.execute("SELECT fact_key, fact_value FROM user_facts").fetchall()
    conn.close()
    return {row["fact_key"]: row["fact_value"] for row in rows}

def save_contact(name: str, phone: str):
    conn = get_connection()
    clean_phone = phone.strip().replace(" ", "").replace("-", "")
    conn.execute("INSERT OR REPLACE INTO custom_contacts (name, phone) VALUES (?, ?)", (name.strip().lower(), clean_phone))
    conn.commit()
    conn.close()

def get_contact_phone(name: str) -> str:
    conn = get_connection()
    row = conn.execute("SELECT phone FROM custom_contacts WHERE name = ?", (name.strip().lower(),)).fetchone()
    conn.close()
    return row["phone"] if row else ""

def log_conversation_turn(user_msg: str, assistant_reply: str, provider: str = "Groq", latency: float = 0.0):
    conn = get_connection()
    conn.execute(
        "INSERT INTO conversation_history (user_msg, assistant_reply, provider, latency) VALUES (?, ?, ?, ?)",
        (user_msg, assistant_reply, provider, latency)
    )
    conn.commit()
    conn.close()

def get_recent_conversations(limit: int = 5) -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT user_msg, assistant_reply FROM conversation_history ORDER BY id DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return [{"user": row["user_msg"], "assistant": row["assistant_reply"]} for row in reversed(rows)]
