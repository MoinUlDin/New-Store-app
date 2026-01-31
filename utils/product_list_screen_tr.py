"""
Translations for ProductListScreen.

Provide translations as a simple dict lookup. Function `t(key, lang)` returns the
translated string for the given language ('en' or 'ur'). If a key is missing the
function returns the key itself (so missing translations are obvious).
"""

from typing import Dict

_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        "search_products_placeholder": "Search by name, barcode or short code",
        "search": "Search",
        "all_companies": "All companies",
        "all_categories": "All categories",
        "refresh": "Refresh",
        "name": "Name",
        "short_code": "Short Code",
        "category": "Category",
        "company": "Company",
        "base_price": "Base",
        "sell_price": "Sell",
        "stock": "Stock / Reorder",
        "actions": "Actions",
        "edit": "Edit",
        "delete": "Delete",
        "confirm_delete_title": "Confirm",
        "confirm_delete_product": "Delete product (id={id})?",
        "deleted": "Deleted",
        "product_deleted": "Product deleted.",
        "error": "Error",
        "reorder": "Reorder",
        "results_for": "results for",
        "kg": 'Kg',
        "gram": 'gm',
        "ltr": 'ltr',
        "show_all": "Show All",
    },
    "ur": {
        "search_products_placeholder": "نام، بارکوڈ یا شارٹ کوڈ سے تلاش کریں",
        "search": "تلاش",
        "all_companies": "تمام کمپنیاں",
        "all_categories": "تمام زمروں",
        "refresh": "تازہ کریں",
        "name": "نام",
        "short_code": "شارٹ کوڈ",
        "category": "زمرہ",
        "company": "کمپنی",
        "base_price": "بنیادی قیمت",
        "sell_price": "فروخت قیمت",
        "stock": "اسٹاک / دوبارہ آرڈر",
        "actions": "عمل",
        "edit": "ترمیم",
        "delete": "حذف",
        "confirm_delete_title": "تصدیق",
        "confirm_delete_product": "کیا آپ واقعی مصنوعات (id={id}) کو حذف کرنا چاہتے ہیں؟",
        "deleted": "حذف شدہ",
        "product_deleted": "مصنوعہ حذف کر دیا گیا۔",
        "error": "خرابی",
        "reorder": "دوبارہ آرڈر",
        "results_for": "نتائج برائے",
        "kg": 'کلوگرام',
        "gm": 'گرام',
        "ltr": 'لیٹر',
        "show_all": "سب دیکھایں",
    },
}


def t(key: str, lang: str = "ur") -> str:
    """
    Translate key for given language.
    - If translation exists, return it.
    - Otherwise return the key (so missing translations are visible).
    """
    if not lang:
        lang = "ur"
    return _TRANSLATIONS.get(lang, {}).get(key, key)
