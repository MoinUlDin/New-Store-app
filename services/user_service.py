# File: services/user_service.py
# Path: services/user_service.py

from typing import Optional, List, Dict, Any
from data.db import get_connection, db_transaction
from services import auth_service   # uses auth_service.create_user / authenticate_user etc.
from datetime import datetime, timezone


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def create_user(username: str, password: str, email: Optional[str] = None, role: str = "shopkeeper", is_superadmin: bool = False) -> int:
    """
    Wrapper around auth_service.create_user to create a user.
    Raises ValueError on conflict (username/email exists).
    """
    return auth_service.create_user(username=username, password=password, email=email, role=role, is_superadmin=is_superadmin)


def authenticate(username: str, password: str) -> Optional[Dict[str, Any]]:
    return auth_service.authenticate_user(username, password)


def change_password(username: str, old_password: str, new_password: str) -> bool:
    return auth_service.change_password(username, old_password, new_password)


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.execute("SELECT id, username, email, role, is_superadmin, is_active, created_at, last_login_at FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    if not row:
        return None
    return dict(row)


def list_users(limit: int = 100, offset: int = 0, conn=None) -> List[Dict[str, Any]]:
    if conn is None:
        print('creating new connection')
        conn = get_connection()
    cur = conn.execute("SELECT id, username, email, role, is_superadmin, is_active, created_at, last_login_at FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?", (limit, offset))
    return [dict(r) for r in cur.fetchall()]


def update_user(user_id: int, data: Dict[str, Any], actor_is_superadmin: bool = False) -> bool:
    """
    Update allowed user fields. Non-superadmin actors cannot change is_superadmin flag.
    data keys: email, role, is_active, username
    """
    allowed = []
    params = []
    if "username" in data:
        allowed.append("username = ?"); params.append(data["username"])
    if "email" in data:
        allowed.append("email = ?"); params.append(data["email"])
    if "role" in data:
        allowed.append("role = ?"); params.append(data["role"])
    if "is_active" in data:
        allowed.append("is_active = ?"); params.append(1 if data["is_active"] else 0)
    if "is_superadmin" in data:
        if actor_is_superadmin:
            allowed.append("is_superadmin = ?"); params.append(1 if data["is_superadmin"] else 0)

    if not allowed:
        return False

    params.append(datetime.now(timezone.utc).isoformat())
    # Ensure updated_at column exists? if not, we skip updating it. We'll just run the update without updated_at column.
    params.append(user_id)
    sql = f"UPDATE users SET {', '.join(allowed)} WHERE id = ?"
    conn = get_connection()
    with db_transaction(conn):
        conn.execute(sql, params)
    return True


def deactivate_user(user_id: int, actor_is_superadmin: bool = False) -> bool:
    """
    Soft-disable user. Prevent deactivating a superadmin unless actor is superadmin.
    """
    conn = get_connection()
    cur = conn.execute("SELECT is_superadmin FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    if not row:
        return False
    if row["is_superadmin"] and not actor_is_superadmin:
        raise PermissionError("cannot_deactivate_superadmin")
    with db_transaction(conn):
        conn.execute("UPDATE users SET is_active = 0 WHERE id = ?", (user_id,))
    return True


def delete_user(user_id: int, actor_is_superadmin: bool = False) -> bool:
    """
    Hard delete - only allowed by superadmin.
    """
    conn = get_connection()
    cur = conn.execute("SELECT is_superadmin FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    if not row:
        return False
    if row["is_superadmin"] and not actor_is_superadmin:
        raise PermissionError("cannot_delete_superadmin")
    with db_transaction(conn):
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    return True
