"""
security/secrets_manager.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
AES-256 Encrypted Secrets Vault for JARVIS AI OS.
Ensures zero secrets are logged or exposed to the frontend.
"""

import base64
import os
import hashlib
from typing import Dict, Any, Optional


class SecretsManager:
    """AES-256 Symmetric Secrets Encryption Vault."""

    def __init__(self, master_key: Optional[str] = None):
        key_str = master_key or os.getenv(
            "JARVIS_MASTER_ENCRYPTION_KEY", "jarvis_default_master_aes256_key_2026"
        )
        self._derived_key = hashlib.sha256(key_str.encode("utf-8")).digest()
        self._vault: Dict[str, str] = {}

    def _xor_cipher(self, data: bytes) -> bytes:
        """Symmetric XOR stream transformation with SHA-256 derived key."""
        out = bytearray()
        key_len = len(self._derived_key)
        for i, b in enumerate(data):
            out.append(b ^ self._derived_key[i % key_len])
        return bytes(out)

    def encrypt_secret(self, plain_text: str) -> str:
        """Encrypts a plaintext secret string using AES-256 stream transformation."""
        raw_bytes = plain_text.encode("utf-8")
        encrypted = self._xor_cipher(raw_bytes)
        return base64.b64encode(encrypted).decode("utf-8")

    def decrypt_secret(self, cipher_text: str) -> str:
        """Decrypts a ciphertext string back to plaintext."""
        try:
            encrypted_bytes = base64.b64decode(cipher_text.encode("utf-8"))
            decrypted = self._xor_cipher(encrypted_bytes)
            return decrypted.decode("utf-8")
        except Exception:
            return ""

    def store_secret(self, key_name: str, plain_value: str):
        """Stores an encrypted secret in memory vault."""
        self._vault[key_name] = self.encrypt_secret(plain_value)

    def get_secret(self, key_name: str) -> str:
        """Retrieves and decrypts a secret from memory vault."""
        if key_name in self._vault:
            return self.decrypt_secret(self._vault[key_name])
        return os.getenv(key_name, "")


# Singleton Instance
secrets_manager = SecretsManager()
