# File: utils/add_update_screen_tr.py

_TRANSLATIONS = {
    "en": {
        "title": "Add New Item",
        "barcode": "Barcode",
        "short_code": "Short Code",
        "item_name_en": "Name (English)",
        "item_name_ur": "Name (Urdu)",
        "category": "Category",
        "company": "Company",
        "base_price": "Base Price",
        "sell_price": "Sell Price",
        "initial_stock": "Stock",
        "packing_size": "Packing Size",
        "supply_pack_qty": "Supply Pack Qty",
        "unit": "Unit",
        "reorder_threshold": "Low Stock Alert",   
    },
    "ur": {
        "title": "نیا آئٹم شامل کریں",
        "barcode": "بار کوڈ",
        "short_code": "شارٹ کوڈ",
        "item_name_en": "نام (انگلش) ",
        "item_name_ur": "نام (اردو) ",
        "category": "جنس",
        "company": "نام کمپنی",
        "base_price": "قیمت خرید",
        "sell_price": "قیمت فروخت",
        "initial_stock": "سٹاک",
        "packing_size": "پیکینگ سائز",
        "supply_pack_qty": "تعداد سپلائی",
        "unit": "یونٹ",
        "reorder_threshold": "کم تعداد", 
    }
}

def t(key: str, lang: str = 'ur') -> str:
    try:
        lang_dict = _TRANSLATIONS.get(lang, _TRANSLATIONS['ur'])
        return lang_dict.get(key, key)
    except Exception:
        return key