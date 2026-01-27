# File: utils/order_screen_tr.py

_TRANSLATIONS = {
    "en": {
        "tokri": "Basket",
        "item": "Item",
        "price": "Price",
        "qty": "Qty",
        "total": "Total",
        "subtotal": "Subtotal",
        "checkout": "Checkout",
        "search_item": "Search Item",
        "search_placeholder": "Scan barcode or enter name/company...",
        "select_category": "Select Category",
        "select_company": "Select Company",
        "add": "Add",
    },
    "ur": {
        "tokri": "ٹوکری",
        "item": "آئٹم",
        "price": "قیمت",
        "qty": "مقدار",
        "total": "ٹوٹل",
        "subtotal": "سب ٹوٹل",
        "checkout": "چیک آؤٹ",
        "search_item": "آئٹم تلاش کریں",
        "search_placeholder": "بار کوڈ اسکین کریں یا نام / کمپنی درج کریں...",
        "select_category": "زمرہ منتخب کریں",
        "select_company": "کمپنی منتخب کریں",
        "add": "شامل کریں",
    }
}

def t(key: str, lang: str = 'ur') -> str:
    try:
        lang_dict = _TRANSLATIONS.get(lang, _TRANSLATIONS['ur'])
        return lang_dict.get(key, key)
    except Exception:
        return key