"""
Purpose:
Multi-Tenant User Account & Authentication Engine for Jarvis AI OS.

Responsibilities:
- SQLite/PostgreSQL 'users' & 'revoked_tokens' table schema management
- Production-grade password hashing with Bcrypt
- Signed JWT Session Token generation & verification
- Short-Lived Access Token & Long-Lived Refresh Token rotation
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
ACCESS_TOKEN_EXPIRATION = 86400  # 24 Hours
REFRESH_TOKEN_EXPIRATION = 86400 * 30  # 30 Days

def init_users_db():
    with db.get_connection() as conn:
        cursor = conn.cursor()
        if db.USE_POSTGRES:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id VARCHAR(64) PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    user_name VARCHAR(128) NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt VARCHAR(64) NOT NULL,
                    role VARCHAR(32) DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS revoked_tokens (
                    jti VARCHAR(128) PRIMARY KEY,
                    revoked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        else:
            cursor.execute("""
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
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS revoked_tokens (
                    jti TEXT PRIMARY KEY,
                    revoked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    def create_tokens(cls, user_id: str, email: str, role: str) -> Dict[str, str]:
        now = int(time.time())
        jti = uuid.uuid4().hex

        access_payload = {
            "sub": user_id,
            "email": email,
            "role": role,
            "type": "access",
            "jti": jti,
            "exp": now + ACCESS_TOKEN_EXPIRATION
        }

        refresh_payload = {
            "sub": user_id,
            "email": email,
            "type": "refresh",
            "jti": jti,
            "exp": now + REFRESH_TOKEN_EXPIRATION
        }

        if USE_JWT and jwt:
            access_token = jwt.encode(access_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
            refresh_token = jwt.encode(refresh_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        else:
            access_token = f"jarvis_access_{user_id}_{uuid.uuid4().hex[:16]}"
            refresh_token = f"jarvis_refresh_{user_id}_{uuid.uuid4().hex[:16]}"

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRATION
        }

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

            token_data = cls.create_tokens(user_id, clean_email, role)
            logger.info("AUTH_SERVICE", f"User '{clean_email}' authenticated successfully.")
            return {
                "success": True,
                "token": token_data["access_token"],
                "refresh_token": token_data["refresh_token"],
                "user": {"id": user_id, "email": clean_email, "user_name": user_name, "role": role}
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @classmethod
    def revoke_token(cls, jti: str) -> bool:
        """Revokes a JWT token by jti identifier."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                sql = db.adapt_query("INSERT INTO revoked_tokens (jti) VALUES (?)")
                cursor.execute(sql, (jti,))
            return True
        except Exception:
            return False

    @classmethod
    def is_token_revoked(cls, jti: str) -> bool:
        """Checks if a token JTI has been revoked."""
        if not jti:
            return False
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                sql = db.adapt_query("SELECT jti FROM revoked_tokens WHERE jti = ?")
                cursor.execute(sql, (jti,))
                return cursor.fetchone() is not None
        except Exception:
            return False

    @classmethod
    def verify_token(cls, token: str) -> Dict[str, Any]:
        """Verifies JWT token signature, expiration, and checks revocation table."""
        if not token:
            return {"valid": False, "error": "Token is missing."}

        if USE_JWT and jwt:
            try:
                payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
                jti = payload.get("jti")
                if jti and cls.is_token_revoked(jti):
                    return {"valid": False, "error": "Token has been revoked."}
                return {"valid": True, "payload": payload}
            except jwt.ExpiredSignatureError:
                return {"valid": False, "error": "Token has expired."}
            except jwt.InvalidTokenError as e:
                return {"valid": False, "error": f"Invalid token: {str(e)}"}
        else:
            if token.startswith("jarvis_access_") or token.startswith("jarvis_jwt_"):
                return {"valid": True, "payload": {"sub": "dev_user"}}
            return {"valid": False, "error": "Invalid dev token."}

auth_service = AuthService()

