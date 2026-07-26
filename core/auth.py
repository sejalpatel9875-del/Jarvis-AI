"""
Purpose:
Multi-Tenant User Account & Authentication Engine for Jarvis AI OS (Sprint v3.0).

Responsibilities:
- SQLite 'users' table schema management
- Password hashing with salted SHA-256
- User registration, authentication, and session token issuance

Dependencies:
- sqlite3, hashlib, os, uuid, secrets
- memory/database.py
- services/logger.py
"""

import os
import uuid
import hashlib
import sqlite3
from typing import Dict, Any, Optional
import memory.database as db
from services.logger import logger

def init_users_db():
    """Initializes SQLite users table if it does not exist."""
    with db.get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                user_name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

# Initialize DB on module import
init_users_db()

class AuthService:
    """User Authentication & Account Management Subsystem."""

    @staticmethod
    def _hash_password(password: str, salt: str) -> str:
        """Generates salted SHA-256 password hash."""
        return hashlib.sha256((password + salt).encode("utf-8")).hexdigest()

    @classmethod
    def register_user(cls, email: str, user_name: str, password: str) -> Dict[str, Any]:
        """Registers a new user account."""
        clean_email = email.strip().lower()
        clean_name = user_name.strip()
        
        if not clean_email or not password:
            return {"success": False, "error": "Email and password are required."}

        salt = uuid.uuid4().hex[:16]
        pwd_hash = cls._hash_password(password, salt)
        user_id = str(uuid.uuid4())[:8]

        try:
            with db.get_connection() as conn:
                conn.execute(
                    "INSERT INTO users (id, email, user_name, password_hash, salt) VALUES (?, ?, ?, ?, ?)",
                    (user_id, clean_email, clean_name, pwd_hash, salt)
                )

            logger.info("AUTH_SERVICE", f"Registered user '{clean_email}' (ID: {user_id})")
            return {
                "success": True,
                "user": {"id": user_id, "email": clean_email, "user_name": clean_name}
            }
        except sqlite3.IntegrityError:
            return {"success": False, "error": f"Account with email '{clean_email}' already exists."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @classmethod
    def login_user(cls, email: str, password: str) -> Dict[str, Any]:
        """Authenticates user credentials and issues session token."""
        clean_email = email.strip().lower()
        
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, user_name, password_hash, salt, role FROM users WHERE email = ?", (clean_email,))
                row = cursor.fetchone()

            if not row:
                return {"success": False, "error": "Invalid email or password."}

            user_id, user_name, stored_hash, salt, role = row
            if cls._hash_password(password, salt) != stored_hash:
                return {"success": False, "error": "Invalid email or password."}

            token = f"jarvis_token_{user_id}_{uuid.uuid4().hex[:12]}"
            logger.info("AUTH_SERVICE", f"User '{clean_email}' authenticated successfully.")
            
            return {
                "success": True,
                "token": token,
                "user": {"id": user_id, "email": clean_email, "user_name": user_name, "role": role}
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

# Global AuthService Singleton
auth_service = AuthService()
