# utils/add_stock_tr.py
# Translation mapping for AddStock (receive packs) screen.
# Usage: from utils.add_stock_tr import t
#        label = t("search", "en")   # -> "Search"
#        label = t("search", "ur")   # -> "تلاش"

TRANSLATIONS = {
    "en": {
        "search_products_placeholder": "Search by name, barcode or short code",
        "search": "Search",
        "refresh": "Refresh",
        "name": "Name",
        "short_code": "Short Code",
        "barcode": "Barcode",
        "company": "Company",
        "stock": "Stock",
        "selected_product": "Selected product:",
        "unit": "Unit:",
        "supply_pack_qty": "Supply / pack:",
        "current_stock": "Current stock:",
        "num_packs": "Packs:",
        "cost_total": "Cost:",
        "reference_id": "Reference ID (optional)",
        "added_qty": "Added qty:",
        "new_stock": "New stock:",
        "receive": "Receive",
        "cancel": "Cancel",
        "validation_title": "Validation",
        "enter_search_term": "Enter a search term.",
        "error": "Error",
        "success": "Success",
        "receive_success_msg": "Stock updated.",
        "select_product_first": "Please select a product first.",
        "price": "Price",
    },
    "ur": {
        "search_products_placeholder": "نام، بارکوڈ یا شارٹ کوڈ سے تلاش کریں",
        "search": "تلاش",
        "refresh": "تازہ کریں",
        "name": "نام",
        "short_code": "شارٹ کوڈ",
        "barcode": "بارکوڈ",
        "company": "کمپنی",
        "stock": "اسٹاک",
        "selected_product": "منتخب شدہ آئٹم:",
        "unit": "یونٹ:",
        "supply_pack_qty": "سپلائی فی پیک:",
        "current_stock": "موجودہ اسٹاک:",
        "num_packs": "پیک:",
        "cost_total": "قیمت:",
        "reference_id": "حوالہ شناخت (اختیاری)",
        "added_qty": "شامل مقدار:",
        "new_stock": "نیا اسٹاک:",
        "receive": "موصول کریں",
        "cancel": "منسوخ",
        "validation_title": "تصدیق",
        "enter_search_term": "براہ کرم تلاش کی عبارت لکھیں۔",
        "error": "خرابی",
        "success": "کامیابی",
        "receive_success_msg": "اسٹاک تازہ ہوا۔",
        "select_product_first": "براہ کرم پہلے کوئی آئٹم منتخب کریں۔",
        "price": "قیمت",
    },
}


def t(key: str, lang: str = "ur") -> str:
    """
    Return translated string for `key` in given `lang` ("ur" or "en").
    If not found, returns the key (so calling code can detect missing translations).
    """
    lang = (lang or "ur").lower()
    if lang not in TRANSLATIONS:
        lang = "ur"
    return TRANSLATIONS.get(lang, {}).get(key, key)
