# File: services/category_service.py
# Path: services/category_service.py

from typing import Optional, List, Dict, Any
from data.db import get_connection, db_transaction
from datetime import datetime, timezone


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def create_category(name: str) -> int:
    conn = get_connection()
    now = _now_iso()
    with db_transaction(conn):
        cur = conn.execute("INSERT INTO categories (name, created_at) VALUES (?, ?)", (name, now))
        return cur.lastrowid


def get_category(category_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
    row = cur.fetchone()
    return dict(row) if row else None


def update_category(category_id: int, name: str) -> bool:
    conn = get_connection()
    now = _now_iso()
    with db_transaction(conn):
        conn.execute("UPDATE categories SET name = ?, created_at = ? WHERE id = ?", (name, now, category_id))
    return True


def delete_category(category_id: int) -> bool:
    conn = get_connection()
    with db_transaction(conn):
        conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
    return True


def list_categories(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.execute("SELECT * FROM categories ORDER BY name LIMIT ? OFFSET ?", (limit, offset))
    return [dict(r) for r in cur.fetchall()]
