# utils/settings_screen_tr.py

_TRANSLATIONS = {
    "en": {
        "system_settings": "System Settings",
        "general": "General",
        "shop_name": "Shop Name",
        "shop_name_ph": "Enter shop name",
        "phone": "Phone",
        "phone_ph": "Enter phone number",
        "address": "Address",
        "address_ph": "Enter shop address",
        "save": "Save",
        "general_saved": "Settings saved.",
        "language": "Language",
        "select_language": "Select language",
        "apply": "Apply",
        "language_applied": "Language applied.",
        "security": "Security",
        "old_password": "Old Password",
        "old_password_ph": "Enter current password",
        "new_password": "New Password",
        "new_password_ph": "Enter new password",
        "confirm_password": "Confirm Password",
        "confirm_password_ph": "Confirm new password",
        "change_password": "Change Password",
        "password_fill": "Please fill all password fields.",
        "password_mismatch": "New and Confirm password do not match.",
        "password_short": "New password is too short.",
        "password_change_failed": "Failed to change password.",
        "password_changed": "Password changed successfully.",
        "password_incorrect": "Old password incorrect or change failed.",
        "font": "Font",

        # Password rules / toggles
        "password_rules_title": "Password Rules",
        "password_rules": "Password Rules",
        "ask_pass_startup": "Ask password on startup",
        "ask_pass_on_product_update": "Ask password when updating product",
        "ask_pass_on_base_price_changed": "Ask password when base price changes",
        "ask_pass_on_sell_price_changed": "Ask password when sell price changes",
        "ask_pass_on_stock_adjustment": "Ask password for stock readjustments",
        "ask_pass_on_new_stock": "Ask password on new stock receipt",
    },
    "ur": {
        "system_settings": "سسٹم کی ترتیب",
        "general": "عام",
        "shop_name": "دکان کا نام",
        "shop_name_ph": "دکان کا نام درج کریں",
        "phone": "فون نمبر",
        "phone_ph": "فون نمبر درج کریں",
        "address": "پتہ",
        "address_ph": "دکان کا پتہ درج کریں",
        "save": "محفوظ کریں",
        "general_saved": "سیٹنگ محفوظ کر دی گئی ہے۔",
        "language": "زبان",
        "select_language": "زبان منتخب کریں",
        "apply": "لاگو کریں",
        "language_applied": "زبان لاگو کر دی گئی۔",
        "security": "سیکیورٹی",
        "old_password": "پرانا پاس ورڈ",
        "old_password_ph": "پرانا پاس ورڈ درج کریں",
        "new_password": "نیا پاس ورڈ",
        "new_password_ph": "نیا پاس ورڈ درج کریں",
        "confirm_password": "پاس ورڈ کی تصدیق کریں",
        "confirm_password_ph": "پاس ورڈ کی تصدیق کریں",
        "change_password": "پاس ورڈ تبدیل کریں",
        "password_fill": "براہ کرم تمام پاس ورڈ فیلڈز پُر کریں۔",
        "password_mismatch": "نیا اور تصدیق شدہ پاس ورڈ میل نہیں کھاتے۔",
        "password_short": "نیا پاس ورڈ بہت چھوٹا ہے۔",
        "password_change_failed": "پاس ورڈ تبدیل نہیں ہو سکا۔",
        "password_changed": "پاس ورڈ کامیابی سے تبدیل ہوگیا۔",
        "password_incorrect": "پرانا پاس ورڈ غلط ہے یا تبدیلی ناکام رہی۔",
        "font": "فونٹ",

        # Password rules / toggles (Urdu)
        "password_rules_title": "پاس ورڈ کے قواعد",
        "password_rules": "پاس ورڈ کی ترتیبات",
        "ask_pass_startup": "اسٹارٹ اپ پر پاس ورڈ پوچھیے",
        "ask_pass_on_product_update": "آئٹم میں تبدیلی پر پاس ورڈ پوچھیے",
        "ask_pass_on_base_price_changed": "قیمت خرید میں تبدیلی پر پاس ورڈ پوچھیے",
        "ask_pass_on_sell_price_changed": "قیمت فروخت میں تبدیلی پر پاس ورڈ پوچھیے",
        "ask_pass_on_stock_adjustment": "سٹاک ایڈجسٹمنٹ پر پاس ورڈ پوچھیے",
        "ask_pass_on_new_stock": "نئی سپلائی وصولی پر پاس ورڈ پوچھیے",
    },
}


def t(key: str, lang: str = "ur") -> str:
    """
    Return translated string for key and language.
    Falls back to Urdu map if language missing, then to key itself.
    """
    try:
        lang_map = _TRANSLATIONS.get(lang, _TRANSLATIONS["ur"])
        return lang_map.get(key, key)
    except Exception:
        return key
