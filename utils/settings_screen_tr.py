# File: utils/settings_screen_tr.py

_TRANSLATIONS = {
    "en": {
        "system_settings": "System Settings",
        "general": "General",
        "shop_name": "Shop Name",
        "save": "Save",
        "language": "Language",
        "security": "Security",
        "old_pass": "Old Password",
        "new_pass": "New Password",
        "confirm_pass": "Confirm Password",
        "font": "Font",
    },
    "ur": {
        "system_settings": "سسٹم کی ترتیب",
        "general": "عام",
        "shop_name": "دکان کا نام",
        "save": "محفوظ کریں",
        "language": "زبان",
        "security": "سیکیورٹی",
        "old_pass": "پرانا پاس ورڈ",
        "new_pass": "نیا پاس ورڈ",
        "confirm_pass": "پاس ورڈ کی تصدیق کریں",
        "font": "فونٹ",
    }
}

def t(key: str, lang: str = 'ur') -> str:
    return _TRANSLATIONS.get(lang, _TRANSLATIONS['ur']).get(key, key)