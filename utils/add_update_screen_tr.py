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
        "initial_stock": "Initial Stock",
        "packing_size": "Packing Size",
        "custom_packing": "Custom Packing",
        "supply_pack_size": "Supply Pack Size",
        "unit": "Unit",
        "reorder_threshold": "Low Stock Alert",   
        'cancel': "Cancel",
        #Unit Options
        "kg": 'Kg', 
        'gm': 'Gm', 
        'ltr': 'Ltr',
        'ml': 'Ml',
        'pcs': 'Pcs',
        
        # placeholders
        "barcode_ph": "Scan or Enter Barcode",
        "short_code_ph": "Enter Short Code",
        
        # buttons
        "save": "Save",
        "update": "Update",
        "clear": "Clear",
        'warnign_cancel': "Cancel",
    
        # Errors
        'name_ur_error': 'Please Provide Urdu Name',
        'base_price_error': 'Base Price Required',
        'sell_price_error': 'Sell Price Required',
        'initial_stock_error': "Initial Stock Required",
        'reorder_error': "Low Stock Alert Required",
        "price_warning": "Price Warning",
        "price_warning_msg": "Sell price is lower than or equal to base price. You won't make a profit!",
        'clear_warning_msg': 'Are you sure you want to clear all fields?',
        'warning': "Warning"
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
        "custom_packing": "کسٹم پیک",
        "supply_pack_size": "سپلائی پیکینگ",
        "unit": "یونٹ",
        "reorder_threshold": "کم تعداد(الرٹ)", 
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
        "clear": "نیا",
        
        # Errors
        'name_ur_error': 'اردو نام ضروری ہے',
        'base_price_error': 'قیمت خرید ضروری ہے',
        'sell_price_error': 'قیمت فروخت ضروری ہے',
        'initial_stock_error': 'سٹاک مقدار ضروری ہے',
        'reorder_error': 'کم تعداد ضروری ہے',
        
        "price_warning": "انتباہ قیمت",
        "price_warning_msg": "قیمت فروخت ، قیمت خرید سے کم یا برابر ہے۔ اس سے آپ کو پرافٹ نہیں ہو گا۔",

        'warnign_cancel': 'نہیں رکو',
        "warning": "انتباہ",
        'clear_warning_msg': 'کیا آپ ایک نیا فارم چاہتے ہیں؟',
    }
}

def t(key: str, lang: str = 'ur') -> str:
    try:
        lang_dict = _TRANSLATIONS.get(lang, _TRANSLATIONS['ur'])
        return lang_dict.get(key, key)
    except Exception:
        return key