"""
memory/vector_memory.py
~~~~~~~~~~~~~~~~~~~~~~~
Lightweight semantic recall for conversation history using TF-IDF-style
keyword vectors stored in SQLite.  No external ML dependencies — tokenisation
is handled with ``re`` and similarity is computed via cosine overlap of
keyword-frequency dicts.

Usage::

    from memory.vector_memory import vector_memory

    vector_memory.save_embedding("What's the weather?", "It's sunny today.", "Groq")
    results = vector_memory.semantic_recall("weather forecast", top_k=3)
"""

from __future__ import annotations

import datetime
import json
import math
import re
from typing import Any, Dict, List

import memory.database as db

# ────────────────────────────────────────────────────────────────────
# Constants
# ────────────────────────────────────────────────────────────────────

_STOP_WORDS: set[str] = {
    "a", "an", "the", "is", "it", "to", "of", "in", "and", "or", "for",
    "on", "at", "by", "with", "from", "as", "this", "that", "was", "are",
    "be", "been", "being", "have", "has", "had", "do", "does", "did",
    "will", "would", "could", "should", "may", "might", "can", "shall",
    "not", "no", "but", "if", "so", "than", "too", "very", "just", "about",
    "up", "out", "my", "your", "its", "his", "her", "our", "their", "me",
    "him", "them", "we", "you", "i", "what", "which", "who", "how", "when",
    "where", "why",
}

_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")

# ────────────────────────────────────────────────────────────────────
# Schema initialisation
# ────────────────────────────────────────────────────────────────────


def _init_vector_table() -> None:
    """Create the ``conversation_vectors`` table if it does not exist."""
    with db.get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversation_vectors (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp   TEXT    NOT NULL,
                user_message TEXT   NOT NULL,
                assistant_reply TEXT NOT NULL,
                keywords    TEXT    NOT NULL,
                provider    TEXT    NOT NULL
            )
        """)
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_cv_timestamp "
            "ON conversation_vectors(timestamp);"
        )


# Auto-create table on module import (mirrors memory.database pattern).
_init_vector_table()

# ────────────────────────────────────────────────────────────────────
# Helper utilities
# ────────────────────────────────────────────────────────────────────


def _tokenize(text: str) -> List[str]:
    """Lowercase tokenisation with stop-word removal.

    Args:
        text: Raw input string.

    Returns:
        List of cleaned tokens suitable for keyword extraction.
    """
    return [
        tok
        for tok in _TOKEN_PATTERN.findall(text.lower())
        if tok not in _STOP_WORDS and len(tok) > 1
    ]


def _build_keyword_vector(text: str) -> Dict[str, float]:
    """Build a normalised term-frequency vector from *text*.

    Each term's raw count is divided by the total number of tokens so that
    vectors of different lengths remain comparable.

    Args:
        text: Concatenated conversation text (user + assistant).

    Returns:
        Dictionary mapping each keyword to its normalised frequency.
    """
    tokens = _tokenize(text)
    if not tokens:
        return {}

    freq: Dict[str, int] = {}
    for tok in tokens:
        freq[tok] = freq.get(tok, 0) + 1

    total = len(tokens)
    return {k: v / total for k, v in freq.items()}


def _cosine_similarity(vec_a: Dict[str, float], vec_b: Dict[str, float]) -> float:
    """Compute cosine similarity between two sparse keyword vectors.

    Args:
        vec_a: First keyword-frequency vector.
        vec_b: Second keyword-frequency vector.

    Returns:
        Similarity score in the range ``[0.0, 1.0]``.
    """
    if not vec_a or not vec_b:
        return 0.0

    common_keys = set(vec_a) & set(vec_b)
    if not common_keys:
        return 0.0

    dot = sum(vec_a[k] * vec_b[k] for k in common_keys)
    mag_a = math.sqrt(sum(v * v for v in vec_a.values()))
    mag_b = math.sqrt(sum(v * v for v in vec_b.values()))

    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0

    return dot / (mag_a * mag_b)


# ────────────────────────────────────────────────────────────────────
# Core class
# ────────────────────────────────────────────────────────────────────


class ConversationVectorMemory:
    """Store and recall conversation turns via keyword-vector similarity.

    Each conversation turn is tokenised into a lightweight TF-style keyword
    vector, serialised as JSON, and persisted in the ``conversation_vectors``
    SQLite table.  Retrieval ranks stored turns against a query using cosine
    similarity over these keyword vectors.
    """

    # ── persistence ──────────────────────────────────────────────────

    def save_embedding(
        self,
        user_msg: str,
        assistant_reply: str,
        provider: str = "Groq",
    ) -> None:
        """Compute and store a keyword vector for a conversation turn.

        Args:
            user_msg:        The user's message text.
            assistant_reply: The assistant's reply text.
            provider:        LLM provider name (e.g. ``"Groq"``).
        """
        combined_text = f"{user_msg} {assistant_reply}"
        keywords = _build_keyword_vector(combined_text)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with db.get_connection() as conn:
            conn.execute(
                "INSERT INTO conversation_vectors "
                "(timestamp, user_message, assistant_reply, keywords, provider) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    timestamp,
                    user_msg,
                    assistant_reply,
                    json.dumps(keywords),
                    provider,
                ),
            )

    # ── retrieval ────────────────────────────────────────────────────

    def semantic_recall(
        self,
        query: str,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Retrieve the most relevant past conversation turns for *query*.

        Computes a keyword vector for the query and ranks every stored
        conversation by cosine similarity, returning the *top_k* best
        matches in descending order of relevance.

        Args:
            query: Natural-language search query.
            top_k: Maximum number of results to return.

        Returns:
            List of dicts, each containing ``id``, ``timestamp``,
            ``user_message``, ``assistant_reply``, ``provider``, and
            ``score`` (float similarity).
        """
        query_vec = _build_keyword_vector(query)
        if not query_vec:
            return []

        with db.get_connection() as conn:
            rows = conn.execute(
                "SELECT id, timestamp, user_message, assistant_reply, "
                "keywords, provider FROM conversation_vectors"
            ).fetchall()

        scored: List[tuple[float, Dict[str, Any]]] = []
        for row in rows:
            stored_vec: Dict[str, float] = json.loads(row["keywords"])
            score = _cosine_similarity(query_vec, stored_vec)
            if score > 0.0:
                scored.append(
                    (
                        score,
                        {
                            "id": row["id"],
                            "timestamp": row["timestamp"],
                            "user_message": row["user_message"],
                            "assistant_reply": row["assistant_reply"],
                            "provider": row["provider"],
                            "score": round(score, 6),
                        },
                    )
                )

        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [entry for _, entry in scored[:top_k]]


# ────────────────────────────────────────────────────────────────────
# Module-level singleton
# ────────────────────────────────────────────────────────────────────

vector_memory = ConversationVectorMemory()
