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
        'cancel': "Cancel",
        #Unit Options
        "kg": 'Kg', 
        'gm': 'Gm', 
        'ltr': 'Ltr',
        'ml': 'Ml',
        'pcs': 'Pcs',
        
        #placeholders
        "barcode_ph": "Scan or Enter Barcode",
        "short_code_ph": "Enter Short Code",
        
        #buttons
        "save": "Save",
        "update": "Update",
        "add": "Add"
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
        'cancel': "منسوخ کریں",
        #Unit Options
        "kg": 'کلوگرام', 
        'gm': 'گرام', 
        'ltr': 'لیٹر',
        'ml': 'ملی لیٹر',
        'pcs': 'پیکٹ',
        
        #placeholders
        "barcode_ph": "بارکوڈ سکن کریں / یا داخل کریں",
        "short_code_ph": "شارٹ کوڈ داخل کریں",
        
        #buttons
        "save": "محفوظ کریں",
        "update": "تبدیل کریں",
        "add": "نیا"
    }
}

def t(key: str, lang: str = 'ur') -> str:
    try:
        lang_dict = _TRANSLATIONS.get(lang, _TRANSLATIONS['ur'])
        return lang_dict.get(key, key)
    except Exception:
        return key