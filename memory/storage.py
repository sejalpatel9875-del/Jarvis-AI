import datetime
from typing import List, Optional
from memory.database import get_connection
from memory.models import ConversationModel, PreferenceModel

def save_conversation(user_message: str, assistant_reply: str, provider: str = "Groq") -> ConversationModel:
    """Saves a conversation turn into SQLite conversations table."""
    conn = get_connection()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO conversations (timestamp, user_message, assistant_reply, provider) VALUES (?, ?, ?, ?)",
        (timestamp, user_message, assistant_reply, provider)
    )
    conv_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return ConversationModel(
        id=conv_id,
        timestamp=timestamp,
        user_message=user_message,
        assistant_reply=assistant_reply,
        provider=provider
    )

def load_recent(limit: int = 10) -> List[ConversationModel]:
    """Loads the most recent conversation turns from database."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, timestamp, user_message, assistant_reply, provider FROM conversations ORDER BY id DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    
    result = [
        ConversationModel(
            id=row["id"],
            timestamp=row["timestamp"],
            user_message=row["user_message"],
            assistant_reply=row["assistant_reply"],
            provider=row["provider"]
        ) for row in reversed(rows)
    ]
    return result

def search_history(query: str, limit: int = 10) -> List[ConversationModel]:
    """Searches past conversation history by keyword matching."""
    conn = get_connection()
    search_pattern = f"%{query.strip()}%"
    rows = conn.execute(
        """SELECT id, timestamp, user_message, assistant_reply, provider 
           FROM conversations 
           WHERE user_message LIKE ? OR assistant_reply LIKE ? 
           ORDER BY id DESC LIMIT ?""",
        (search_pattern, search_pattern, limit)
    ).fetchall()
    conn.close()
    
    return [
        ConversationModel(
            id=row["id"],
            timestamp=row["timestamp"],
            user_message=row["user_message"],
            assistant_reply=row["assistant_reply"],
            provider=row["provider"]
        ) for row in rows
    ]

def save_preference(key: str, value: str):
    """Saves or updates a user preference in SQLite database."""
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO preferences (key, value) VALUES (?, ?)",
        (key.strip().lower(), value.strip())
    )
    conn.commit()
    conn.close()

def get_preference(key: str, default: str = "") -> str:
    """Retrieves a user preference from SQLite database."""
    conn = get_connection()
    row = conn.execute("SELECT value FROM preferences WHERE key = ?", (key.strip().lower(),)).fetchone()
    conn.close()
    return row["value"] if row else default
