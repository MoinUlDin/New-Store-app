# File: services/stock_service.py
# Path: services/stock_service.py

from decimal import Decimal
from typing import Optional
from data.db import get_connection, db_transaction, sqlite3
from services.audit_service import log_audit
from datetime import datetime, timezone


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


# services/stock_service.py

def record_movement(
    product_id: int,
    qty: Decimal,
    reason: str,
    created_by: Optional[int] = None,
    reference_id: Optional[str] = None,
    related_doc: Optional[str] = None,
    unit: Optional[str] = None,
    cost_total: Optional[Decimal] = None,
    conn: Optional[sqlite3.Connection] = None,
) -> int:
    """
    Record a stock movement and atomically update product.stock_qty.
    Uses existing connection if provided.
    """

    own_conn = False

    if conn is None:
        conn = get_connection()
        own_conn = True

    now = _now_iso()
    db_qty = float(qty)
    db_cost = float(cost_total) if cost_total is not None else None

    try:
        with db_transaction(conn):

            # insert movement
            cur = conn.execute(
                """
                INSERT INTO stock_movements
                (product_id, qty, reason, reference_id, related_doc, unit, cost_total, created_at, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    product_id,
                    db_qty,
                    reason,
                    reference_id,
                    related_doc,
                    unit,
                    db_cost,
                    now,
                    created_by,
                ),
            )

            # update stock
            conn.execute(
                """
                UPDATE products
                SET stock_qty = stock_qty + ?, updated_at = ?
                WHERE id = ?
                """,
                (db_qty, now, product_id),
            )

            return cur.lastrowid

    finally:
        if own_conn:
            conn.close()


def consume_for_sale(
    product_id: int,
    qty: Decimal,
    sale_id: int,
    created_by: Optional[int] = None,
    conn: Optional[sqlite3.Connection] = None,
):
    """
    Consume stock for a sale using shared connection.
    """
    return record_movement(
        product_id=product_id,
        qty=-qty,
        reason="sale",
        created_by=created_by,
        reference_id=str(sale_id),
        conn=conn,
    )

def receive_packs(product_id: int, num_packs: int, cost_total: Optional[Decimal] = None, created_by: Optional[int] = None, reference_id: Optional[str] = None):
    """
    Use products.supply_pack_qty to compute the base unit quantity added.
    """
    conn = get_connection()
    cur = conn.execute("SELECT supply_pack_qty FROM products WHERE id = ?", (product_id,))
    row = cur.fetchone()
    pack_qty = Decimal(str(row["supply_pack_qty"])) if row and row["supply_pack_qty"] is not None else Decimal("1")
    qty = pack_qty * Decimal(num_packs)
    return record_movement(product_id=product_id, qty=qty, reason="purchase_receipt", created_by=created_by, reference_id=reference_id, cost_total=cost_total)

