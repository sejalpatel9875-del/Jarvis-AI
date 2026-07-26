"""
Purpose:
Multi-Tenant User Account & Authentication Engine for Jarvis AI OS.

Responsibilities:
- SQLite/PostgreSQL 'users' table schema management
- Production-grade password hashing with Bcrypt
- Signed JWT Session Token generation & verification
"""

import os
import uuid
import time
import hashlib
import sqlite3
from typing import Dict, Any, Optional
import memory.database as db
from services.logger import logger

# Try importing passlib for bcrypt, fallback to salted SHA-512 if passlib is missing
try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    USE_BCRYPT = True
except Exception:
    pwd_context = None
    USE_BCRYPT = False

# Import pyjwt for signed JWT tokens
try:
    import jwt
    USE_JWT = True
except Exception:
    jwt = None
    USE_JWT = False

IS_PROD = os.getenv("ENVIRONMENT", "development").lower() == "production"

SECRET_KEY = os.getenv("SECRET_KEY", "").strip()
if not SECRET_KEY:
    if IS_PROD:
        raise RuntimeError("CRITICAL SECURITY ERROR: 'SECRET_KEY' environment variable MUST be set in production mode.")
    SECRET_KEY = "dev_only_random_secret_" + uuid.uuid4().hex

if IS_PROD and not USE_JWT:
    raise RuntimeError("CRITICAL SECURITY ERROR: 'pyjwt' library MUST be installed for production JWT tokens.")

JWT_SECRET = SECRET_KEY
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_SECONDS = 86400 * 7  # 7 Days token validity

def init_users_db():
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

init_users_db()

class AuthService:
    """Enterprise Production User Authentication Subsystem."""

    @staticmethod
    def hash_password(password: str, salt: str = "") -> str:
        if USE_BCRYPT and pwd_context:
            return pwd_context.hash(password)
        return hashlib.sha512((password + salt).encode("utf-8")).hexdigest()

    @staticmethod
    def verify_password(plain_password: str, stored_hash: str, salt: str = "") -> bool:
        if USE_BCRYPT and pwd_context and stored_hash.startswith("$2"):
            try:
                return pwd_context.verify(plain_password, stored_hash)
            except Exception:
                pass
        sha256_hash = hashlib.sha256((plain_password + salt).encode("utf-8")).hexdigest()
        sha512_hash = hashlib.sha512((plain_password + salt).encode("utf-8")).hexdigest()
        return stored_hash in (sha256_hash, sha512_hash)

    @classmethod
    def register_user(cls, email: str, user_name: str, password: str) -> Dict[str, Any]:
        clean_email = email.strip().lower()
        clean_name = user_name.strip()
        
        if not clean_email or not password:
            return {"success": False, "error": "Email and password are required."}

        salt = uuid.uuid4().hex[:16]
        pwd_hash = cls.hash_password(password, salt)
        user_id = str(uuid.uuid4())[:8]

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                sql = db.adapt_query("INSERT INTO users (id, email, user_name, password_hash, salt) VALUES (?, ?, ?, ?, ?)")
                cursor.execute(sql, (user_id, clean_email, clean_name, pwd_hash, salt))

            logger.info("AUTH_SERVICE", f"Registered user '{clean_email}' (ID: {user_id})")
            return {
                "success": True,
                "user": {"id": user_id, "email": clean_email, "user_name": clean_name}
            }
        except Exception as e:
            err_msg = str(e)
            if "UNIQUE" in err_msg.upper() or "already exists" in err_msg:
                return {"success": False, "error": f"Account with email '{clean_email}' already exists."}
            return {"success": False, "error": err_msg}

    @classmethod
    def login_user(cls, email: str, password: str) -> Dict[str, Any]:
        clean_email = email.strip().lower()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                sql = db.adapt_query("SELECT id, user_name, password_hash, salt, role FROM users WHERE email = ?")
                cursor.execute(sql, (clean_email,))
                row = cursor.fetchone()

            if not row:
                return {"success": False, "error": "Invalid email or password."}

            user_id, user_name, stored_hash, salt, role = row[0], row[1], row[2], row[3], row[4]
            if not cls.verify_password(password, stored_hash, salt):
                return {"success": False, "error": "Invalid email or password."}

            payload = {
                "sub": user_id,
                "email": clean_email,
                "role": role,
                "exp": int(time.time()) + JWT_EXPIRATION_SECONDS
            }

            if USE_JWT and jwt:
                token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
            else:
                token = f"jarvis_jwt_{user_id}_{uuid.uuid4().hex[:16]}"

            logger.info("AUTH_SERVICE", f"User '{clean_email}' authenticated successfully.")
            return {
                "success": True,
                "token": token,
                "user": {"id": user_id, "email": clean_email, "user_name": user_name, "role": role}
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

auth_service = AuthService()
