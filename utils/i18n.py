# utils/i18n.py

from PyQt6.QtCore import Qt
from services.settings_service import get_setting


_TRANSLATIONS = {
    "en": {
        "app_title": "Kiryana Store Management",
        "orders": "Orders",
        "products": "Products",
        "reports": "Reports",
        "settings": "Settings",
        "new_item": "New Item",
        "new_order": "New Order",
        "stock_list": "Stock List",
        # stocks related
        "stock_list": "Stock List",
        "add_stock": 'Add Stock',
        "manage_stock": "Change Stock",
        "dashboard": "Dashboard",
    },

    "ur": {
        "app_title": "کریانہ اسٹور مینجمنٹ",
        "orders": "آرڈر",
        "products": "پراڈکٹس",
        "reports": "رپورٹس",
        "settings": "ترتیب",
        #order related
        "new_item": "نیا آئٹم",
        "new_order": "نیا آرڈر",
        # stocks related
        "stock_list": "سٹاک لسٹ",
        "add_stock": "نیا سٹاک",
        "manage_stock": "سٹاک تبدیلی",
        "dashboard": "ڈیش بورڈ",
    }
}


def t(key: str, lang:str = 'ur') -> str:

    try:
        return _TRANSLATIONS.get(lang, {}).get(key, key)
    except Exception:
        return key


