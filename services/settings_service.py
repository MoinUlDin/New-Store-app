# File: services/settings_service.py
# Path: services/settings_service.py

from typing import Optional, Dict
import sqlite3
from data.db import get_connection, db_transaction
from datetime import datetime, timezone


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def get_setting(key: str) -> Optional[str]:
    conn = get_connection()
    cur = conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cur.fetchone()
    return row["value"] if row else None


def set_setting(key: str, value: str) -> None:
    conn = get_connection()
    now = _now_iso()
    with db_transaction(conn):
        cur = conn.execute("SELECT key FROM settings WHERE key = ?", (key,))
        if cur.fetchone():
            conn.execute("UPDATE settings SET value = ?, updated_at = ? WHERE key = ?", (value, now, key))
        else:
            conn.execute("INSERT INTO settings (key, value, created_at, updated_at) VALUES (?, ?, ?, ?)",
                         (key, value, now, now))


def get_all_settings() -> Dict[str, str]:
    conn = get_connection()
    cur = conn.execute("SELECT key, value FROM settings")
    return {r["key"]: r["value"] for r in cur.fetchall()}


def initialize_defaults(defaults: Dict[str, str]) -> None:
    """
    Apply defaults only when keys do not exist.
    """
    conn = get_connection()
    now = _now_iso()
    with db_transaction(conn):
        for k, v in defaults.items():
            cur = conn.execute("SELECT key FROM settings WHERE key = ?", (k,))
            if not cur.fetchone():
                conn.execute("INSERT INTO settings (key, value, created_at, updated_at) VALUES (?, ?, ?, ?)",
                             (k, v, now, now))
