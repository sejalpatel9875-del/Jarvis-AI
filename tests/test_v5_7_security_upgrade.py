"""
tests/test_v5_7_security_upgrade.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Comprehensive Unittest Suite for Enterprise Security Upgrade (v5.7.0).
"""

import unittest
import time
from security.auth_manager import auth_manager
from security.secrets_manager import secrets_manager
from security.middleware import SecurityMiddleware


class TestV57SecurityUpgrade(unittest.TestCase):
    def test_jwt_access_and_refresh_token_rotation(self):
        # 1. Access Token Generation & Validation
        access_token = auth_manager.create_access_token(user_id="user_admin", role="owner")
        self.assertIsNotNone(access_token)
        payload = auth_manager.validate_access_token(access_token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload["sub"], "user_admin")
        self.assertEqual(payload["role"], "owner")

        # 2. Refresh Token Rotation
        refresh_token = auth_manager.create_refresh_token(user_id="user_admin")
        self.assertIsNotNone(refresh_token)

        rotation_res = auth_manager.rotate_refresh_token(refresh_token)
        self.assertIsNotNone(rotation_res)
        self.assertIn("access_token", rotation_res)
        self.assertIn("refresh_token", rotation_res)

        # Confirm old refresh token is revoked
        reused_res = auth_manager.rotate_refresh_token(refresh_token)
        self.assertIsNone(reused_res)

    def test_pbkdf2_password_hashing(self):
        pwd = "JarvisSecurePassword2026!"
        hashed = auth_manager._hash_password(pwd)
        self.assertTrue(auth_manager.verify_password(pwd, hashed["hash"], hashed["salt"]))
        self.assertFalse(
            auth_manager.verify_password("WrongPassword", hashed["hash"], hashed["salt"])
        )

    def test_secrets_manager_aes256_encryption(self):
        raw_secret = "sk_live_jarvis_enterprise_key_9988"
        encrypted = secrets_manager.encrypt_secret(raw_secret)
        self.assertNotEqual(raw_secret, encrypted)
        decrypted = secrets_manager.decrypt_secret(encrypted)
        self.assertEqual(raw_secret, decrypted)

    def test_input_sanitization_xss_and_sqli(self):
        middleware = SecurityMiddleware(app=None)

        # XSS Script stripping
        malicious_xss = "Hello <script>alert('hacked')</script> World"
        clean_xss = middleware.sanitize_input(malicious_xss)
        self.assertNotIn("<script>", clean_xss)

        # SQL Injection comment stripping
        malicious_sqli = "SELECT * FROM users WHERE id = 1; -- DROP TABLE users"
        clean_sqli = middleware.sanitize_input(malicious_sqli)
        self.assertNotIn(";", clean_sqli)
        self.assertNotIn("--", clean_sqli)

    def test_token_revocation(self):
        token = auth_manager.create_access_token("user_test")
        self.assertIsNotNone(auth_manager.validate_access_token(token))
        auth_manager.revoke_token(token)
        self.assertIsNone(auth_manager.validate_access_token(token))


if __name__ == "__main__":
    unittest.main()
