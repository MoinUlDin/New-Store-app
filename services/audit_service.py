# File: services/audit_service.py
# Path: services/audit_service.py

from typing import Optional
from data.db import get_connection
from datetime import datetime, timezone


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def log_audit(conn_or_none=None, entity_type: str = "", action: str = "", details: str = "", created_at: Optional[str] = None):
    """
    If conn_or_none is a sqlite3.Connection, will reuse it (useful inside transactions).
    Otherwise obtain a new connection and insert.
    """
    own_conn = False
    if created_at is None:
        created_at = _now_iso()

    if conn_or_none is None:
        conn = get_connection()
        own_conn = True
    else:
        conn = conn_or_none

    conn.execute("INSERT INTO audit_logs (entity_type, action, details, created_at) VALUES (?, ?, ?, ?)",
                 (entity_type, action, details, created_at))

    if own_conn:
        conn.commit()
