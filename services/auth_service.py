"""
services/auth_service.py

Auth-related service functions:
- create_user
- authenticate_user
- change_password
- request_password_reset
- verify_reset_token
- consume_reset_token

Uses data/db.py for DB connection, transactions and password helpers.
"""

from typing import Optional, Dict, Any
import sqlite3
from datetime import datetime, timezone, timedelta
import secrets
import hashlib
import os

from data.db import (
    get_connection,
    db_transaction,
    PBKDF2_ITERATIONS,
    SALT_BYTES,
)

# local helpers for hashing (kept consistent with data/db.py)
def _hash_password(password: str, salt: bytes = None):
    if salt is None:
        salt = os.urandom(SALT_BYTES)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return key.hex(), salt.hex()


def verify_password(password: str, password_hash_hex: str, salt_hex: str) -> bool:
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), PBKDF2_ITERATIONS)
    return key.hex() == password_hash_hex


def get_user_by_username(conn: sqlite3.Connection, username: str) -> Optional[sqlite3.Row]:
    cur = conn.execute("SELECT * FROM users WHERE username = ?", (username,))
    return cur.fetchone()


def get_user_by_email(conn: sqlite3.Connection, email: str) -> Optional[sqlite3.Row]:
    cur = conn.execute("SELECT * FROM users WHERE email = ?", (email,))
    return cur.fetchone()


def create_user(username: str, password: str, email: Optional[str] = None, role: str = "shopkeeper", is_superadmin: bool = False) -> int:
    """
    Create a new user. Raises ValueError if username or email already exists.
    Returns created user id.
    """
    conn = get_connection()
    with db_transaction(conn):
        cur = conn.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cur.fetchone():
            raise ValueError("username_exists")

        if email:
            cur = conn.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cur.fetchone():
                raise ValueError("email_exists")

        pwd_hash, salt = _hash_password(password)
        now = datetime.now(timezone.utc).isoformat()
        cur = conn.execute(
            "INSERT INTO users (username, email, password_hash, salt, role, is_superadmin, is_active, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (username, email, pwd_hash, salt, role, 1 if is_superadmin else 0, 1, now),
        )
        return cur.lastrowid


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Verify credentials. If valid, update last_login_at and return user dict (without password).
    Returns None on failure.
    """
    conn = get_connection()
    cur = conn.execute("SELECT * FROM users WHERE username = ? AND is_active = 1", (username,))
    row = cur.fetchone()
    if not row:
        return None

    if not verify_password(password, row["password_hash"], row["salt"]):
        return None

    now = datetime.now(timezone.utc).isoformat()
    with db_transaction(conn):
        conn.execute("UPDATE users SET last_login_at = ? WHERE id = ?", (now, row["id"]))

    # build user dict (do not include password_hash/salt)
    user = {k: row[k] for k in row.keys() if k not in ("password_hash", "salt")}
    return user


def change_password(username: str, old_password: str, new_password: str) -> bool:
    """
    Change a user's password by verifying old_password first.
    Returns True on success, False if authentication failed.
    """
    conn = get_connection()
    cur = conn.execute("SELECT id, password_hash, salt FROM users WHERE username = ? AND is_active = 1", (username,))
    row = cur.fetchone()
    if not row:
        return False

    if not verify_password(old_password, row["password_hash"], row["salt"]):
        return False

    pwd_hash, salt = _hash_password(new_password)
    with db_transaction(conn):
        conn.execute("UPDATE users SET password_hash = ?, salt = ? WHERE id = ?", (pwd_hash, salt, row["id"]))
    return True


# ---------------- Password reset flows ----------------

RESET_TOKEN_TTL = timedelta(hours=1)  # token valid for 1 hour


def request_password_reset(email: str) -> Optional[str]:
    """
    Create a password reset token for the given email.
    Returns the token (which should be emailed to the user) or None if user not found.
    """
    conn = get_connection()
    cur = conn.execute("SELECT id FROM users WHERE email = ? AND is_active = 1", (email,))
    row = cur.fetchone()
    if not row:
        return None

    user_id = row["id"]
    token = secrets.token_urlsafe(32)
    expires_at = (datetime.now(timezone.utc) + RESET_TOKEN_TTL).isoformat()
    now = datetime.now(timezone.utc).isoformat()

    with db_transaction(conn):
        conn.execute(
            "INSERT INTO password_resets (user_id, token, expires_at, used, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, token, expires_at, 0, now),
        )

    return token


def verify_reset_token(token: str) -> Optional[int]:
    """
    Check token exists, not used and not expired.
    Returns user_id if valid, otherwise None.
    """
    conn = get_connection()
    cur = conn.execute("SELECT id, user_id, expires_at, used FROM password_resets WHERE token = ?", (token,))
    row = cur.fetchone()
    if not row:
        return None

    if row["used"]:
        return None

    expires_at = datetime.fromisoformat(row["expires_at"])
    if datetime.now(timezone.utc) > expires_at:
        return None

    return row["user_id"]


def consume_reset_token(token: str, new_password: str) -> bool:
    """
    If token valid, mark as used and update user's password.
    Returns True on success.
    """
    conn = get_connection()
    cur = conn.execute("SELECT id, user_id, expires_at, used FROM password_resets WHERE token = ?", (token,))
    row = cur.fetchone()
    if not row or row["used"]:
        return False

    expires_at = datetime.fromisoformat(row["expires_at"])
    if datetime.now(timezone.utc) > expires_at:
        return False

    # update password and mark token used atomically
    pwd_hash, salt = _hash_password(new_password)
    now = datetime.now(timezone.utc).isoformat()

    with db_transaction(conn):
        conn.execute("UPDATE users SET password_hash = ?, salt = ? WHERE id = ?", (pwd_hash, salt, row["user_id"]))
        conn.execute("UPDATE password_resets SET used = 1 WHERE id = ?", (row["id"],))

    return True
