import threading
import datetime
import json
from typing import List, Optional, Dict, Any
import memory.database as db
from memory.models import ConversationModel, PreferenceModel
from memory.vector_memory import _build_keyword_vector, _cosine_similarity

class MemoryManager:
    """
    Public interface for Upgraded Jarvis Memory Engine.
    Handles Conversation, Preferences, Task, Knowledge, Session, and Long-Term Memory.
    Uses thread-safe operations, SQLite/PostgreSQL connections, and semantic search.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MemoryManager, cls).__new__(cls)
                cls._instance._pref_cache = {}
                cls._instance._session_cache = {}
            return cls._instance

    # ────────────────────────────────────────────────────────────────────
    # General Semantic Search Helper
    # ────────────────────────────────────────────────────────────────────

    def _semantic_search_table(
        self,
        table_name: str,
        query: str,
        keyword_col: str = "keywords",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieves and ranks records using sparse keyword vector similarity."""
        query_vec = _build_keyword_vector(query)
        if not query_vec:
            return []

        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(db.adapt_query(f"SELECT * FROM {table_name}"))
            rows = cursor.fetchall()

        scored = []
        for r in rows:
            row_dict = dict(r)
            kw_str = row_dict.get(keyword_col)
            if kw_str:
                try:
                    stored_vec = json.loads(kw_str)
                except Exception:
                    stored_vec = {}
                score = _cosine_similarity(query_vec, stored_vec)
                if score > 0.0:
                    row_dict["score"] = round(score, 6)
                    scored.append((score, row_dict))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [item for _, item in scored[:limit]]

    # ────────────────────────────────────────────────────────────────────
    # 1. Conversation Memory (Backward Compatible)
    # ────────────────────────────────────────────────────────────────────

    def save_turn(self, user_message: str, assistant_reply: str, provider: str = "Groq") -> ConversationModel:
        """Saves a conversation turn into both standard and structured memory tables."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        combined_text = f"{user_message} {assistant_reply}"
        keywords = _build_keyword_vector(combined_text)
        kw_str = json.dumps(keywords)

        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Save into legacy conversations table
            sql_legacy = db.adapt_query(
                "INSERT INTO conversations (timestamp, user_message, assistant_reply, provider) VALUES (?, ?, ?, ?)"
            )
            cursor.execute(sql_legacy, (timestamp, user_message, assistant_reply, provider))
            legacy_id = cursor.lastrowid

            # Save into upgraded conversation_memory table
            sql_upgraded = db.adapt_query(
                "INSERT INTO conversation_memory (timestamp, user_message, assistant_reply, keywords, provider) VALUES (?, ?, ?, ?, ?)"
            )
            cursor.execute(sql_upgraded, (timestamp, user_message, assistant_reply, kw_str, provider))

        return ConversationModel(
            id=legacy_id,
            timestamp=timestamp,
            user_message=user_message,
            assistant_reply=assistant_reply,
            provider=provider
        )

    def get_recent(self, limit: int = 10) -> List[ConversationModel]:
        """Loads the most recent conversation turns from history."""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            sql = db.adapt_query(
                "SELECT id, timestamp, user_message, assistant_reply, provider FROM conversations ORDER BY id DESC LIMIT ?"
            )
            cursor.execute(sql, (limit,))
            rows = cursor.fetchall()

        return [
            ConversationModel(
                id=row["id"],
                timestamp=row["timestamp"],
                user_message=row["user_message"],
                assistant_reply=row["assistant_reply"],
                provider=row["provider"]
            ) for row in reversed(rows)
        ]

    def search(self, query: str, limit: int = 10) -> List[ConversationModel]:
        """Searches past conversation history semantically."""
        results = self._semantic_search_table("conversation_memory", query, limit=limit)
        return [
            ConversationModel(
                id=res.get("id"),
                timestamp=res.get("timestamp", ""),
                user_message=res.get("user_message", ""),
                assistant_reply=res.get("assistant_reply", ""),
                provider=res.get("provider", "Groq")
            ) for res in results
        ]

    # ────────────────────────────────────────────────────────────────────
    # 2. User Preferences
    # ────────────────────────────────────────────────────────────────────

    def save_preference(self, key: str, value: str):
        """Saves a preference in persistent storage and updates local cache."""
        self.save_user_preference(key, value)

    def get_preference(self, key: str, default: str = "") -> str:
        """Retrieves a preference value."""
        return self.get_user_preference(key, default)

    def save_user_preference(self, key: str, value: str, category: str = "general"):
        """Saves or updates a preference safely in legacy and upgraded tables."""
        clean_key = key.strip().lower()
        clean_val = value.strip()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with db.get_connection() as conn:
            cursor = conn.cursor()
            # Legacy save
            sql_legacy = db.adapt_query("INSERT OR REPLACE INTO preferences (key, value) VALUES (?, ?)")
            cursor.execute(sql_legacy, (clean_key, clean_val))

            # Upgraded save
            sql_upgraded = db.adapt_query(
                "INSERT INTO user_preferences_memory (timestamp, key, value, category) VALUES (?, ?, ?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value = EXCLUDED.value, timestamp = EXCLUDED.timestamp, category = EXCLUDED.category"
            )
            cursor.execute(sql_upgraded, (timestamp, clean_key, clean_val, category))

        self._pref_cache[clean_key] = clean_val

    def get_user_preference(self, key: str, default: str = "") -> str:
        """Retrieves a user preference value."""
        clean_key = key.strip().lower()
        if clean_key in self._pref_cache:
            return self._pref_cache[clean_key]

        with db.get_connection() as conn:
            cursor = conn.cursor()
            sql = db.adapt_query("SELECT value FROM user_preferences_memory WHERE key = ?")
            cursor.execute(sql, (clean_key,))
            row = cursor.fetchone()

        val = row["value"] if row else default
        self._pref_cache[clean_key] = val
        return val

    # ────────────────────────────────────────────────────────────────────
    # 3. Task Memory
    # ────────────────────────────────────────────────────────────────────

    def save_task_run(self, task_id: str, goal: str, steps: list, status: str, current_step: int = 0):
        """Saves or updates stateful execution task memory."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        steps_str = json.dumps(steps)

        with db.get_connection() as conn:
            cursor = conn.cursor()
            sql = db.adapt_query(
                "INSERT INTO task_memory (timestamp, task_id, goal, steps_json, status, current_step) VALUES (?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET status = EXCLUDED.status, current_step = EXCLUDED.current_step, timestamp = EXCLUDED.timestamp"
            )
            cursor.execute(sql, (timestamp, str(task_id), goal, steps_str, status, current_step))

    def get_task_run(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves task details dictionary by ID."""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            sql = db.adapt_query("SELECT * FROM task_memory WHERE task_id = ? ORDER BY id DESC LIMIT 1")
            cursor.execute(sql, (str(task_id),))
            row = cursor.fetchone()

        if row:
            r = dict(row)
            r["steps"] = json.loads(r["steps_json"])
            return r
        return None

    def semantic_search_tasks(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Searches task memories semantically based on goals."""
        query_vec = _build_keyword_vector(query)
        if not query_vec:
            return []

        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(db.adapt_query("SELECT id, timestamp, task_id, goal, status, steps_json FROM task_memory"))
            rows = cursor.fetchall()

        scored = []
        for r in rows:
            row_dict = dict(r)
            goal_vec = _build_keyword_vector(row_dict.get("goal", ""))
            score = _cosine_similarity(query_vec, goal_vec)
            if score > 0.0:
                row_dict["score"] = round(score, 6)
                row_dict["steps"] = json.loads(row_dict["steps_json"])
                scored.append((score, row_dict))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [item for _, item in scored[:limit]]

    # ────────────────────────────────────────────────────────────────────
    # 4. Knowledge Memory
    # ────────────────────────────────────────────────────────────────────

    def save_knowledge_fact(self, chunk_id: str, source: str, content: str):
        """Saves a knowledge fact chunk safely."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        keywords = _build_keyword_vector(content)
        kw_str = json.dumps(keywords)

        with db.get_connection() as conn:
            cursor = conn.cursor()
            sql = db.adapt_query(
                "INSERT INTO knowledge_memory (timestamp, chunk_id, source, content, keywords) VALUES (?, ?, ?, ?, ?) "
                "ON CONFLICT(chunk_id) DO UPDATE SET content = EXCLUDED.content, timestamp = EXCLUDED.timestamp, keywords = EXCLUDED.keywords"
            )
            cursor.execute(sql, (timestamp, chunk_id, source, content, kw_str))

    def semantic_search_knowledge(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Searches knowledge chunks semantically."""
        return self._semantic_search_table("knowledge_memory", query, limit=limit)

    # ────────────────────────────────────────────────────────────────────
    # 5. Session Memory (In-Memory Fast Cache + Db Backup)
    # ────────────────────────────────────────────────────────────────────

    def save_session_variable(self, session_id: str, key: str, value: str):
        """Stores a temporary variables in session memory."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sess_id = str(session_id)
        clean_key = key.strip().lower()

        # Update in-memory cache
        if sess_id not in self._session_cache:
            self._session_cache[sess_id] = {}
        self._session_cache[sess_id][clean_key] = value

        # DB backup
        with db.get_connection() as conn:
            cursor = conn.cursor()
            sql = db.adapt_query(
                "INSERT INTO session_memory (timestamp, session_id, key, value) VALUES (?, ?, ?, ?) "
                "ON CONFLICT(session_id, key) DO UPDATE SET value = EXCLUDED.value, timestamp = EXCLUDED.timestamp"
            )
            cursor.execute(sql, (timestamp, sess_id, clean_key, value))

    def get_session_variable(self, session_id: str, key: str, default: Any = None) -> Any:
        """Retrieves a session variable value."""
        sess_id = str(session_id)
        clean_key = key.strip().lower()

        if sess_id in self._session_cache and clean_key in self._session_cache[sess_id]:
            return self._session_cache[sess_id][clean_key]

        with db.get_connection() as conn:
            cursor = conn.cursor()
            sql = db.adapt_query("SELECT value FROM session_memory WHERE session_id = ? AND key = ?")
            cursor.execute(sql, (sess_id, clean_key))
            row = cursor.fetchone()

        val = row["value"] if row else default
        if sess_id not in self._session_cache:
            self._session_cache[sess_id] = {}
        self._session_cache[sess_id][clean_key] = val
        return val

    # ────────────────────────────────────────────────────────────────────
    # 6. Long-Term Memory
    # ────────────────────────────────────────────────────────────────────

    def save_long_term_fact(self, key: str, abstract_summary: str):
        """Stores abstract long term memory summaries safely."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        keywords = _build_keyword_vector(abstract_summary)
        kw_str = json.dumps(keywords)

        with db.get_connection() as conn:
            cursor = conn.cursor()
            sql = db.adapt_query(
                "INSERT INTO long_term_memory (timestamp, key, abstract_summary, keywords) VALUES (?, ?, ?, ?) "
                "ON CONFLICT(key) DO UPDATE SET abstract_summary = EXCLUDED.abstract_summary, timestamp = EXCLUDED.timestamp, keywords = EXCLUDED.keywords"
            )
            cursor.execute(sql, (timestamp, key, abstract_summary, kw_str))

    def semantic_search_long_term(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Searches long term abstract summaries semantically."""
        return self._semantic_search_table("long_term_memory", query, limit=limit)

# Global MemoryManager Singleton Instance
_default_manager = MemoryManager()

# Standalone backward-compatible helper functions
def save_turn(user_message: str, assistant_reply: str, provider: str = "Groq") -> ConversationModel:
    return _default_manager.save_turn(user_message, assistant_reply, provider=provider)

def get_recent(limit: int = 10) -> List[ConversationModel]:
    return _default_manager.get_recent(limit=limit)

def save_preference(key: str, value: str):
    _default_manager.save_preference(key, value)

def get_preference(key: str, default: str = "") -> str:
    return _default_manager.get_preference(key, default=default)
