# main.py
import os
import sys
from typing import Optional

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QObject, pyqtSignal
from PyQt6.QtGui import QFontDatabase, QFont

from app.main_window import MainWindow

from data.db import bootstrap
from services.settings_service import get_setting, set_setting
from services.user_service import list_users

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


class LanguageManager(QObject):
    """
    Central language controller. Attach an instance to the QApplication
    (app.language_manager) so UI screens can connect to language_changed.
    """
    language_changed = pyqtSignal(str)

    def __init__(self, app: QApplication, default: str = "ur"):
        super().__init__()
        self.app = app
        self._current = default

        # preload fonts map (font_name -> file path)
        fonts_dir = os.path.join(PROJECT_ROOT, "resources", "fonts")
        self.font_files = {
            "ur": os.path.join(fonts_dir, "JAMEEL_NOORI.TTF"),
            "en": os.path.join(fonts_dir, "Inter.ttf"),  # optional - if present
        }
        # loaded families cache
        self._families = {}

        # attempt to load fonts (if present)
        for key, path in self.font_files.items():
            if os.path.exists(path):
                fid = QFontDatabase.addApplicationFont(path)
                if fid != -1:
                    families = QFontDatabase.applicationFontFamilies(fid)
                    if families:
                        self._families[key] = families[0]

    @property
    def current(self) -> str:
        return self._current

    def apply_language(self, lang: str):
        """
        Apply language to QApplication: set font and layout direction.
        This does not change translations (strings) — widgets should re-apply
        their labels when they receive the language_changed signal.
        """
        if lang not in ("ur", "en"):
            lang = "ur"

        self._current = lang

        # Set layout direction
        if lang == "en":
            self.app.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        else:
            self.app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        # Apply font if we have loaded one
        family = self._families.get(lang)
        if family:
            # choose a reasonable default point size; widgets can override
            font = QFont(family)
            # for Urdu fonts we might want a larger default due to glyph size
            if lang == "ur":
                font.setPointSize(14)
            else:
                font.setPointSize(12)
            self.app.setFont(font)
        else:
            # fallback: leave QApplication font as-is or set a generic fallback
            if lang == "ur":
                # If Jameel Nori missing, try system fallback but ensure RTL direction applied
                # (we already set LayoutDirection above)
                pass

        # Emit signal so UIs can refresh text / placeholders etc.
        self.language_changed.emit(lang)

    def set_language(self, lang: str):
        """
        Persist language selection to settings and apply immediately.
        """
        if lang not in ("ur", "en"):
            raise ValueError("invalid language")

        # persist
        set_setting("language", lang)
        # apply
        self.apply_language(lang)


def setup_language_manager(app: QApplication) -> LanguageManager:
    """
    Create a LanguageManager, attach it to app and apply current language (from DB).
    """
    # read from settings service; fallback to 'ur' if not set
    lang = get_setting("language") or "ur"
    lm = LanguageManager(app, default=lang)
    # attach to QApplication so other parts can access it:
    app.language_manager = lm
    # apply language now
    lm.apply_language(lang)
    return lm


def main():
    # Initialize DB & seed accounts (bootstrap returns a connection).
    conn = bootstrap(ensure_accounts={
        'superadmin_email': 'moinuldinc@gmail.com',
        'superadmin_username': 'moinuldin',
        'superadmin_password': 'Abnsbghh.147',
        'shopkeeper_email': 'moinuldinc+1@gmail.com',
        'shopkeeper_username': 'admin',
        'shopkeeper_password': 'admin'
    })

    # close the bootstrap connection if you no longer need it
    conn.close()


    # Start Qt app
    app = QApplication(sys.argv)

    # Setup LanguageManager & apply language (loads fonts + sets layout direction)
    lang_mgr = setup_language_manager(app)

    # Create main window
    window = MainWindow()
    window.show()
    window.showMaximized()

    # Example: connect main window to language changes if it exposes an apply_language(lang) method
    # Many widgets will implement a method like apply_language(lang) or on_language_changed.
    if hasattr(window, "apply_language") and callable(getattr(window, "apply_language")):
        lang_mgr.language_changed.connect(lambda l: window.apply_language(l))
    else:
        # fallback: if your MainWindow implements a named slot, connect it here, e.g.:
        # lang_mgr.language_changed.connect(window.on_language_changed)
        pass

    # Make LanguageManager globally available via QApplication.instance()
    # (already set as app.language_manager in setup_language_manager)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
