# File: services/settings_service.py
# Path: services/settings_service.py

from typing import Optional, Dict, Any
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

def set_general(data: Dict[str, str]) -> None:
    """
    Batch-update general settings (shop_name, shop_phone, shop_address)
    in a single transaction with a single SELECT to detect existing keys.
    Missing keys in `data` will be written as empty strings.
    """
    keys = ["shop_name", "shop_phone", "shop_address"]
    items = [(k, str(data.get(k, "") or "")) for k in keys]
    now = _now_iso()
    conn = get_connection()
    with db_transaction(conn):
        placeholders = ",".join("?" for _ in keys)
        cur = conn.execute(f"SELECT key FROM settings WHERE key IN ({placeholders})", tuple(keys))
        existing = {r["key"] for r in cur.fetchall()}

        for k, v in items:
            if k in existing:
                conn.execute(
                    "UPDATE settings SET value = ?, updated_at = ? WHERE key = ?",
                    (v, now, k),
                )
            else:
                conn.execute(
                    "INSERT INTO settings (key, value, created_at, updated_at) VALUES (?, ?, ?, ?)",
                    (k, v, now, now),
                )


def set_password_rules(data: Dict[str, Any]) -> None:
    """
    Batch-update password-rule settings in a single transaction.

    Expected keys (all optional in `data`; missing keys become '0'):
      - pass_on_startup
      - pass_on_product_update
      - pass_on_base_price_changed
      - pass_on_sell_price_changed   <- new key
      - pass_on_stock_adjustment
      - pass_on_new_stock

    Values accepted: bool, "1"/"0", "true"/"false", numbers; normalized to "1" or "0".
    """
    def _normalize(val: Any) -> str:
        if isinstance(val, bool):
            return "1" if val else "0"
        if val is None:
            return "0"
        s = str(val).strip().lower()
        if s in ("1", "true", "yes", "y", "on"):
            return "1"
        return "0"

    keys = [
        "pass_on_startup",
        "pass_on_product_update",
        "pass_on_base_price_changed",
        "pass_on_sell_price_changed",  # newly added key
        "pass_on_stock_adjustment",
        "pass_on_new_stock",
    ]

    items = [(k, _normalize(data.get(k))) for k in keys]
    now = _now_iso()
    conn = get_connection()
    with db_transaction(conn):
        placeholders = ",".join("?" for _ in keys)
        cur = conn.execute(f"SELECT key FROM settings WHERE key IN ({placeholders})", tuple(keys))
        existing = {r["key"] for r in cur.fetchall()}

        for k, v in items:
            if k in existing:
                conn.execute(
                    "UPDATE settings SET value = ?, updated_at = ? WHERE key = ?",
                    (v, now, k),
                )
            else:
                conn.execute(
                    "INSERT INTO settings (key, value, created_at, updated_at) VALUES (?, ?, ?, ?)",
                    (k, v, now, now),
                )



