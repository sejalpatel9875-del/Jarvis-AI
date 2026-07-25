"""
Purpose:
Acts as the public interface for Jarvis Memory Engine.

Responsibilities:
- Thread-safe Singleton instance management
- In-memory preference caching for fast O(1) lookups
- Save conversations and load history
- Public bridge between Brain and Storage layer

Dependencies:
- storage.py
- models.py
"""

import threading
from typing import List, Optional
import memory.storage as storage
from memory.models import ConversationModel, PreferenceModel

class MemoryManager:
    """
    Public interface for Jarvis Memory Engine with Singleton pattern and In-Memory Caching.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MemoryManager, cls).__new__(cls)
                cls._instance._pref_cache = {}
            return cls._instance

    def save_turn(self, user_message: str, assistant_reply: str, provider: str = "Groq") -> ConversationModel:
        """Saves a conversation turn into persistent memory."""
        return storage.save_conversation(user_message, assistant_reply, provider=provider)

    def get_recent(self, limit: int = 10) -> List[ConversationModel]:
        """Loads the most recent conversation turns from history."""
        return storage.load_recent(limit=limit)

    def search(self, query: str, limit: int = 10) -> List[ConversationModel]:
        """Searches past conversation history by keyword."""
        return storage.search_history(query, limit=limit)

    def save_preference(self, key: str, value: str):
        """Saves a preference in persistent storage and updates local cache."""
        clean_key = key.strip().lower()
        clean_val = value.strip()
        storage.save_preference(clean_key, clean_val)
        self._pref_cache[clean_key] = clean_val

    def get_preference(self, key: str, default: str = "") -> str:
        """Retrieves a preference (hits in-memory cache first, falls back to SQLite)."""
        clean_key = key.strip().lower()
        if clean_key in self._pref_cache:
            return self._pref_cache[clean_key]
            
        val = storage.get_preference(clean_key, default=default)
        self._pref_cache[clean_key] = val
        return val

# Global MemoryManager Singleton Instance
_default_manager = MemoryManager()

# Standalone helper functions
def save_turn(user_message: str, assistant_reply: str, provider: str = "Groq") -> ConversationModel:
    return _default_manager.save_turn(user_message, assistant_reply, provider=provider)

def get_recent(limit: int = 10) -> List[ConversationModel]:
    return _default_manager.get_recent(limit=limit)

def save_preference(key: str, value: str):
    _default_manager.save_preference(key, value)

def get_preference(key: str, default: str = "") -> str:
    return _default_manager.get_preference(key, default=default)
