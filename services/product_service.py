"""
services/product_service.py

Product CRUD and search operations.
Uses Decimal internally for monetary and quantity fields.
"""

from decimal import Decimal, InvalidOperation
from typing import Optional, Dict, Any, List
import sqlite3

from data.db import get_connection, db_transaction


def _to_decimal(value) -> Decimal:
    if value is None:
        return Decimal("0")
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return Decimal("0")


def create_product(data: Dict[str, Any]) -> int:
    """
    Create product and return new id.
    data keys expected (some optional):
      short_code, ur_name, en_name, company, barcode,
      base_price (Decimal or numeric), sell_price, stock_qty,
      reorder_threshold, category_id, unit, custom_packing (bool),
      packing_size, supply_pack_qty
    """
    conn = get_connection()
    base_price = float(_to_decimal(data.get("base_price")))
    sell_price = float(_to_decimal(data.get("sell_price")))
    stock_qty = float(_to_decimal(data.get("stock_qty")))
    reorder_threshold = float(_to_decimal(data.get("reorder_threshold")))
    packing_size = float(_to_decimal(data.get("packing_size"))) if data.get("packing_size") is not None else None
    supply_pack_qty = float(_to_decimal(data.get("supply_pack_qty"))) if data.get("supply_pack_qty") is not None else 1.0

    now = __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()

    with db_transaction(conn):
        cur = conn.execute(
            """
            INSERT INTO products
            (short_code, ur_name, en_name, company, barcode, base_price, sell_price, stock_qty, reorder_threshold,
             category_id, unit, custom_packing, packing_size, supply_pack_qty, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("short_code"),
                data.get("ur_name"),
                data.get("en_name"),
                data.get("company"),
                data.get("barcode"),
                base_price,
                sell_price,
                stock_qty,
                reorder_threshold,
                data.get("category_id"),
                data.get("unit", "kg"),
                1 if data.get("custom_packing") else 0,
                packing_size,
                supply_pack_qty,
                now,
                now,
            ),
        )
        return cur.lastrowid


def get_product(product_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cur.fetchone()
    if not row:
        return None

    return {
        "id": row["id"],
        "short_code": row["short_code"],
        "ur_name": row["ur_name"],
        "en_name": row["en_name"],
        "company": row["company"],
        "barcode": row["barcode"],
        "base_price": Decimal(str(row["base_price"])) if row["base_price"] is not None else Decimal("0"),
        "sell_price": Decimal(str(row["sell_price"])) if row["sell_price"] is not None else Decimal("0"),
        "stock_qty": Decimal(str(row["stock_qty"])) if row["stock_qty"] is not None else Decimal("0"),
        "reorder_threshold": Decimal(str(row["reorder_threshold"])) if row["reorder_threshold"] is not None else Decimal("0"),
        "category_id": row["category_id"],
        "unit": row["unit"],
        "custom_packing": bool(row["custom_packing"]),
        "packing_size": Decimal(str(row["packing_size"])) if row["packing_size"] is not None else None,
        "supply_pack_qty": Decimal(str(row["supply_pack_qty"])) if row["supply_pack_qty"] is not None else Decimal("1"),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def update_product(product_id: int, data: Dict[str, Any]) -> bool:
    conn = get_connection()
    fields = []
    params = []

    mapping = {
        "short_code": "short_code",
        "ur_name": "ur_name",
        "en_name": "en_name",
        "company": "company",
        "barcode": "barcode",
        "base_price": lambda v: float(_to_decimal(v)),
        "sell_price": lambda v: float(_to_decimal(v)),
        "stock_qty": lambda v: float(_to_decimal(v)),
        "reorder_threshold": lambda v: float(_to_decimal(v)),
        "category_id": "category_id",
        "unit": "unit",
        "custom_packing": lambda v: 1 if v else 0,
        "packing_size": lambda v: float(_to_decimal(v)) if v is not None else None,
        "supply_pack_qty": lambda v: float(_to_decimal(v)),
    }

    for key, mapper in mapping.items():
        if key in data:
            value = data[key]
            if callable(mapper):
                fields.append(f"{key} = ?")
                params.append(mapper(value))
            else:
                fields.append(f"{mapper} = ?")
                params.append(value)

    if not fields:
        return False

    now = __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()
    fields.append("updated_at = ?")
    params.append(now)
    params.append(product_id)

    sql = f"UPDATE products SET {', '.join(fields)} WHERE id = ?"
    with db_transaction(conn):
        conn.execute(sql, params)
    return True


def delete_product(product_id: int) -> bool:
    conn = get_connection()
    with db_transaction(conn):
        conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
    return True


def list_products(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.execute("SELECT id FROM products ORDER BY ur_name LIMIT ? OFFSET ?", (limit, offset))
    rows = cur.fetchall()
    results = []
    for r in rows:
        prod = get_product(r["id"])
        if prod:
            results.append(prod)
    return results


def search_products(term: str, limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_connection()
    t = f"%{term}%"
    cur = conn.execute(
        "SELECT id FROM products WHERE ur_name LIKE ? OR en_name LIKE ? OR barcode LIKE ? OR short_code LIKE ? LIMIT ?",
        (t, t, t, t, limit),
    )
    rows = cur.fetchall()
    return [get_product(r["id"]) for r in rows]
