# utils/confirm_password_tr.py
# Simple translator for the Confirm Password dialog.
# Usage: from utils.confirm_password_tr import t
#        text = t("confirm_password_title", "ur")

_translations = {
    "en": {
        "confirm_password_title": "Confirm password",
        "confirm_password_prompt": "Enter your password to continue",
        "enter_password_ph": "Password",
        "show": "Show",
        "hide": "Hide",
        "confirm": "Confirm",
        "cancel": "Cancel",
        "validation_title": "Validation",
        "enter_password_warning": "Please enter your password.",
        "error": "Error",
        "failed_read_current_user": "Failed to read current user:\n{err}",
        "no_current_user": "No current user is set. Please login first.",
        "auth_error": "Authentication error",
        "auth_error_detail": "Authentication error:\n{err}",
        "auth_failed": "Authentication failed",
        "invalid_password_no_attempts": "Invalid password. No attempts left.",
        "invalid_password_attempts": "Invalid password. Attempts left: {n}",
    },
    "ur": {
        "confirm_password_title": "پاس ورڈ کی تصدیق کریں",
        "confirm_password_prompt": "جاری رکھنے کے لیے اپنا پاس ورڈ درج کریں",
        "enter_password_ph": "پاس ورڈ",
        "show": "دکھائیں",
        "hide": "چھپائیں",
        "confirm": "تصدیق کریں",
        "cancel": "منسوخ کریں",
        "validation_title": "تصدیق",
        "enter_password_warning": "براہِ کرم اپنا پاس ورڈ درج کریں۔",
        "error": "خرابی",
        "failed_read_current_user": "موجودہ صارف پڑھنے میں ناکام:\n{err}",
        "no_current_user": "کوئی موجودہ صارف سیٹ نہیں ہے۔ براہِ کرم پہلے لاگ اِن کریں۔",
        "auth_error": "تصدیق کی خرابی",
        "auth_error_detail": "تصدیق کی خرابی:\n{err}",
        "auth_failed": "تصدیق ناکام",
        "invalid_password_no_attempts": "غلط پاس ورڈ۔ مزید کوششیں باقی نہیں ہیں۔",
        "invalid_password_attempts": "غلط پاس ورڈ۔ کوششیں باقی: {n}",
    },
}


def t(key: str, lang: str = "en", **fmt) -> str:
    """
    Simple translator lookup.
    - key: translation key
    - lang: 'en' or 'ur' (falls back to 'en' then to key)
    - fmt: optional format replacements (e.g. err=..., n=...)
    """
    if not lang:
        lang = "en"
    # try requested language
    lang_map = _translations.get(lang, {})
    text = lang_map.get(key)
    if text is None:
        # fallback to English
        text = _translations.get("en", {}).get(key, key)
    # apply formatting if placeholders present
    try:
        if fmt and ("{" in text):
            return text.format(**fmt)
        return text
    except Exception:
        return text
