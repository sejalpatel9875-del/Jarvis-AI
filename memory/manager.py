"""
Purpose:
Acts as the public interface for Jarvis Memory.

Responsibilities:
- Save conversations
- Load recent history
- Manage user preferences

Dependencies:
- storage.py
"""

from typing import List, Optional
import memory.storage as storage
from memory.models import ConversationModel, PreferenceModel

class MemoryManager:
    """
    Public interface for Jarvis Memory Engine.
    Connects Brain to Memory Storage API.
    """
    def __init__(self):
        pass

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
        """Saves or updates a user preference in persistent storage."""
        storage.save_preference(key, value)

    def get_preference(self, key: str, default: str = "") -> str:
        """Retrieves a user preference from persistent storage."""
        return storage.get_preference(key, default=default)

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
