"""
security/auth_manager.py
~~~~~~~~~~~~~~~~~~~~~~~~~
JWT & Refresh Token Authentication Manager for JARVIS AI OS.
"""

import time
import base64
import hashlib
import hmac
import json
import uuid
from typing import Dict, Any, Optional

SECRET_KEY = "jarvis_super_secret_jwt_key_change_in_production_32bytes"
ACCESS_TOKEN_EXPIRE_SECONDS = 900  # 15 Minutes
REFRESH_TOKEN_EXPIRE_SECONDS = 604800  # 7 Days


class AuthManager:
    """Handles JWT generation, validation, refresh token rotation, and password hashing."""

    def __init__(self):
        self.revoked_tokens = set()
        self.refresh_token_store = {}  # token -> {user_id, expires_at}

    def _hash_password(self, password: str, salt: Optional[str] = None) -> Dict[str, str]:
        """Hashes passwords securely using PBKDF2-HMAC-SHA256."""
        if not salt:
            salt = uuid.uuid4().hex
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
        return {"hash": base64.b64encode(key).decode("utf-8"), "salt": salt}

    def verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """Verifies password against stored PBKDF2 hash."""
        computed = self._hash_password(password, salt)
        return hmac.compare_digest(computed["hash"], password_hash)

    def _base64url_encode(self, data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")

    def _base64url_decode(self, data_str: str) -> bytes:
        padding = "=" * (4 - (len(data_str) % 4))
        return base64.urlsafe_b64decode((data_str + padding).encode("utf-8"))

    def create_access_token(self, user_id: str, role: str = "employee") -> str:
        """Generates a short-lived (15 min) JWT Access Token."""
        header = {"alg": "HS256", "typ": "JWT"}
        payload = {
            "sub": user_id,
            "role": role,
            "iat": int(time.time()),
            "exp": int(time.time()) + ACCESS_TOKEN_EXPIRE_SECONDS,
            "jti": uuid.uuid4().hex,
        }

        header_b64 = self._base64url_encode(json.dumps(header).encode("utf-8"))
        payload_b64 = self._base64url_encode(json.dumps(payload).encode("utf-8"))

        signature_input = f"{header_b64}.{payload_b64}".encode("utf-8")
        signature = hmac.new(SECRET_KEY.encode("utf-8"), signature_input, hashlib.sha256).digest()
        sig_b64 = self._base64url_encode(signature)

        return f"{header_b64}.{payload_b64}.{sig_b64}"

    def create_refresh_token(self, user_id: str) -> str:
        """Generates a long-lived (7 days) Refresh Token."""
        token = f"ref_{uuid.uuid4().hex}_{int(time.time())}"
        self.refresh_token_store[token] = {
            "user_id": user_id,
            "expires_at": time.time() + REFRESH_TOKEN_EXPIRE_SECONDS,
        }
        return token

    def validate_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validates JWT access token signature, expiration, and revocation status."""
        if token in self.revoked_tokens:
            return None

        parts = token.split(".")
        if len(parts) != 3:
            return None

        header_b64, payload_b64, sig_b64 = parts

        try:
            signature_input = f"{header_b64}.{payload_b64}".encode("utf-8")
            expected_sig = hmac.new(
                SECRET_KEY.encode("utf-8"), signature_input, hashlib.sha256
            ).digest()
            actual_sig = self._base64url_decode(sig_b64)

            if not hmac.compare_digest(expected_sig, actual_sig):
                return None

            payload_bytes = self._base64url_decode(payload_b64)
            payload = json.loads(payload_bytes.decode("utf-8"))

            if time.time() > payload.get("exp", 0):
                return None

            return payload
        except Exception:
            return None

    def rotate_refresh_token(self, old_refresh_token: str) -> Optional[Dict[str, str]]:
        """Revokes old refresh token and issues a new access + refresh token pair."""
        if old_refresh_token not in self.refresh_token_store:
            return None

        data = self.refresh_token_store[old_refresh_token]
        if time.time() > data["expires_at"]:
            del self.refresh_token_store[old_refresh_token]
            return None

        user_id = data["user_id"]
        # Revoke old refresh token
        del self.refresh_token_store[old_refresh_token]

        # Issue new token pair
        new_access = self.create_access_token(user_id)
        new_refresh = self.create_refresh_token(user_id)

        return {
            "access_token": new_access,
            "refresh_token": new_refresh,
            "expires_in": ACCESS_TOKEN_EXPIRE_SECONDS,
        }

    def revoke_token(self, token: str):
        """Adds a token to the revocation list."""
        self.revoked_tokens.add(token)


# Singleton Instance
auth_manager = AuthManager()
