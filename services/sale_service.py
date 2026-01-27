# File: services/sale_service.py
# Path: services/sale_service.py

from decimal import Decimal
from typing import List, Dict, Any, Optional
from data.db import get_connection, db_transaction
from services.stock_service import consume_for_sale
from services.audit_service import log_audit
from datetime import datetime, timezone


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def create_sale(created_by: Optional[int], items: List[Dict[str, Any]], payment_method: Optional[str] = None, note: Optional[str] = None) -> int:
    """
    Create a sale and sale_items, and deduct stock for each item in one transaction.
    items: list of dicts with keys: product_id, qty (Decimal/number), price_per_unit (Decimal/number), base_price_per_unit (Decimal/number), line_discount (Decimal)
    Returns sale_id
    """
    conn = get_connection()
    now = _now_iso()

    # compute totals
    total_before = Decimal('0')
    total_discount = Decimal('0')
    total_tax = Decimal('0')  # tax handling left to caller
    for it in items:
        qty = Decimal(str(it.get("qty", 0)))
        price = Decimal(str(it.get("price_per_unit", 0)))
        discount = Decimal(str(it.get("line_discount", 0)))
        total_before += qty * price
        total_discount += discount
    charged = total_before - total_discount + total_tax

    with db_transaction(conn):
        cur = conn.execute(
            "INSERT INTO sales (created_at, created_by, total_before_discounts, discount, tax, charged_total, payment_method, note) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (now, created_by, float(total_before), float(total_discount), float(total_tax), float(charged), payment_method, note)
        )
        sale_id = cur.lastrowid

        # insert sale_items and consume stock
        for it in items:
            product_id = it["product_id"]
            qty = Decimal(str(it["qty"]))
            price = Decimal(str(it.get("price_per_unit", 0)))
            base_price = Decimal(str(it.get("base_price_per_unit", 0)))
            line_discount = Decimal(str(it.get("line_discount", 0)))
            line_total = qty * price - line_discount

            conn.execute(
                "INSERT INTO sale_items (sale_id, product_id, qty, input_unit, price_per_unit, base_price_per_unit, line_total, line_cost_total, line_discount, line_charged, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (sale_id, product_id, float(qty), it.get("input_unit"), float(price), float(base_price), float(line_total), 0.0, float(line_discount), float(line_total), now)
            )

            # deduct stock (use stock_service)
            consume_for_sale(product_id=product_id, qty=qty, sale_id=sale_id, created_by=created_by, conn=conn)

        # audit
        try:
            log_audit(conn, entity_type="sale", action="create", details=f"sale_id={sale_id}, created_by={created_by}", created_at=now)
        except Exception:
            pass

    return sale_id
