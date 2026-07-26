"""
API Key Management Service for J.A.R.V.I.S. AI OS.

Provides secure generation, hashing, validation, and listing of workspace API keys.
Stores key hashes and metadata into SQLite via memory.database.
"""

import hashlib
import secrets
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List
import memory.database as db
from services.logger import logger


class APIKeyService:
    """Service for managing workspace API keys, key validation, and secret key hashing."""

    def __init__(self) -> None:
        """Initialise APIKeyService and ensure table schema exists."""
        self._init_db()

    def _init_db(self) -> None:
        """Initialise the workspace_api_keys SQLite table and indexes."""
        try:
            with db.get_connection() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS workspace_api_keys (
                        key_id TEXT PRIMARY KEY,
                        workspace_id TEXT NOT NULL,
                        key_hash TEXT UNIQUE NOT NULL,
                        key_prefix TEXT NOT NULL,
                        name TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    )
                """)
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_api_keys_ws ON workspace_api_keys(workspace_id);"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON workspace_api_keys(key_hash);"
                )
        except Exception as e:
            logger.error("API_KEY_SERVICE", f"Failed to initialize database table: {e}")

    def generate_key(self, workspace_id: str, name: str) -> Dict[str, Any]:
        """Generate a new raw API key formatted as 'jarvis_sk_...' and store its SHA-256 hash.

        Args:
            workspace_id: Unique identifier of the workspace owning the key.
            name: Human-readable label or description for the key.

        Returns:
            Dict containing success status, raw secret key (only returned once upon creation),
            key_id, workspace_id, key_prefix, name, and created_at timestamp.
        """
        if not workspace_id or not str(workspace_id).strip():
            return {"success": False, "error": "Workspace ID cannot be empty."}
        if not name or not str(name).strip():
            return {"success": False, "error": "Key name cannot be empty."}

        key_id = f"key_{uuid.uuid4().hex[:12]}"
        raw_key = f"jarvis_sk_{secrets.token_hex(16)}"
        key_hash = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
        key_prefix = raw_key[:13]
        created_at = datetime.now(timezone.utc).isoformat()

        try:
            with db.get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO workspace_api_keys (key_id, workspace_id, key_hash, key_prefix, name, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (key_id, workspace_id, key_hash, key_prefix, name.strip(), created_at),
                )

            logger.info(
                "API_KEY_SERVICE",
                f"Generated API key '{name}' (ID: {key_id}) for workspace '{workspace_id}'",
            )
            return {
                "success": True,
                "key_id": key_id,
                "workspace_id": workspace_id,
                "raw_key": raw_key,
                "key_prefix": key_prefix,
                "name": name.strip(),
                "created_at": created_at,
            }
        except Exception as e:
            logger.error("API_KEY_SERVICE", f"Failed to generate API key: {e}")
            return {"success": False, "error": str(e)}

    def validate_key(self, raw_key: str) -> Dict[str, Any]:
        """Validate a raw API key string by checking its SHA-256 hash in the database.

        Args:
            raw_key: Raw API key string starting with 'jarvis_sk_'.

        Returns:
            Dict containing 'valid' boolean and 'workspace_id' string (or None if invalid).
        """
        if not raw_key or not isinstance(raw_key, str) or not raw_key.strip():
            return {"valid": False, "workspace_id": None}

        key_hash = hashlib.sha256(raw_key.strip().encode("utf-8")).hexdigest()

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT key_id, workspace_id, name, created_at
                    FROM workspace_api_keys
                    WHERE key_hash = ?
                    """,
                    (key_hash,),
                )
                row = cursor.fetchone()

            if row:
                return {
                    "valid": True,
                    "workspace_id": row["workspace_id"],
                    "key_id": row["key_id"],
                    "name": row["name"],
                }
            else:
                return {"valid": False, "workspace_id": None}
        except Exception as e:
            logger.error("API_KEY_SERVICE", f"Failed to validate API key: {e}")
            return {"valid": False, "workspace_id": None}

    def list_keys(self, workspace_id: str) -> List[Dict[str, Any]]:
        """List metadata for all API keys belonging to a workspace.

        Args:
            workspace_id: Unique identifier for the workspace.

        Returns:
            List of dictionaries containing key metadata (key_id, workspace_id, key_prefix, name, created_at).
            Raw secret keys and key hashes are omitted for security.
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT key_id, workspace_id, key_prefix, name, created_at
                    FROM workspace_api_keys
                    WHERE workspace_id = ?
                    ORDER BY created_at DESC
                    """,
                    (workspace_id,),
                )
                rows = cursor.fetchall()
                return [
                    {
                        "key_id": row["key_id"],
                        "workspace_id": row["workspace_id"],
                        "key_prefix": row["key_prefix"],
                        "name": row["name"],
                        "created_at": row["created_at"],
                    }
                    for row in rows
                ]
        except Exception as e:
            logger.error(
                "API_KEY_SERVICE",
                f"Failed to list API keys for workspace '{workspace_id}': {e}",
            )
            return []


# Singleton instance
api_key_service = APIKeyService()
