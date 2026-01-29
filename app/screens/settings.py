# app/screens/setting_screen.py
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QApplication, QGroupBox, QFormLayout,
    QComboBox, QMessageBox, QSizePolicy, QSpacerItem, QCheckBox, QHBoxLayout,
    QScrollArea,
)
from PyQt6.QtCore import Qt

from utils.settings_screen_tr import t  # translator: t(key, lang)
from services import settings_service
from services import user_service


class SettingScreen(QWidget):
    """
    Settings screen:
      - Left column: General (shop_name, phone, address) + Language selector
      - Right column: Password Rules (toggles) above Security (old/new/confirm)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._lang = "ur"
        self._build_ui()
        self._wire_language_manager()
        self.load_settings()
        self.apply_language(self._lang)

    # ---------------- UI builders ----------------
    def _build_ui(self):
        # Create a content widget that holds the two-column layout.
        content = QWidget()
        # main_layout is now the layout of the content widget (not self)
        self.main_layout = QHBoxLayout(content)
        self.main_layout.setContentsMargins(12, 12, 12, 12)
        self.main_layout.setSpacing(16)

        # Left column
        self._build_left_column()

        # Right column
        self._build_right_column()

        left_container = QWidget()
        left_container.setLayout(self.left_col)
        right_container = QWidget()
        right_container.setLayout(self.right_col)

        # add left/right containers to the content layout
        self.main_layout.addWidget(left_container, 3)
        self.main_layout.addWidget(right_container, 2)

        # Put the content widget into a scroll area so the screen gets scrollbars
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setWidget(content)

        # Give the SettingScreen a simple outer layout that contains the scroll area
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(scroll)

        # Keep styles and signals as before
        self._apply_styles()
        self._connect_signals()



    def _build_left_column(self):
        self.left_col = QVBoxLayout()
        self.left_col.setSpacing(12)

        # GENERAL
        self.general_box = QGroupBox()
        self.general_box.setContentsMargins(10, 50, 10, 10)
        general_layout = QFormLayout()
        # general_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.general_box.setLayout(general_layout)

        self.lbl_shop_name = QLabel()
        self.txt_shop_name = QLineEdit()

        self.lbl_phone = QLabel()
        self.txt_phone = QLineEdit()

        self.lbl_address = QLabel()
        self.txt_address = QLineEdit()

        general_layout.addRow(self.lbl_shop_name, self.txt_shop_name)
        general_layout.addRow(self.lbl_phone, self.txt_phone)
        general_layout.addRow(self.lbl_address, self.txt_address)

        self.btn_save_general = QPushButton()
        self.btn_save_general.setFixedWidth(140)
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        btn_row.addWidget(self.btn_save_general)

        self.left_col.addWidget(self.general_box)
        self.left_col.addLayout(btn_row)

        # LANGUAGE
        self.lang_box = QGroupBox()
        lang_layout = QFormLayout()
        self.lang_box.setLayout(lang_layout)

        self.lbl_lang = QLabel()
        self.cmb_lang = QComboBox()
        self.cmb_lang.addItem("اردو", userData="ur")
        self.cmb_lang.addItem("English", userData="en")

        lang_layout.addRow(self.lbl_lang, self.cmb_lang)

        self.btn_apply_lang = QPushButton()
        self.btn_apply_lang.setFixedWidth(140)
        lang_btn_row = QHBoxLayout()
        lang_btn_row.addStretch(1)
        lang_btn_row.addWidget(self.btn_apply_lang)

        self.left_col.addWidget(self.lang_box)
        self.left_col.addLayout(lang_btn_row)

        self.left_col.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

    def _build_right_column(self):
        self.right_col = QVBoxLayout()
        self.right_col.setSpacing(10)

        # PASSWORD RULES (create label widgets for each checkbox)
        self.rules_box = QGroupBox()
        rules_layout = QFormLayout()
        rules_layout.setSpacing(16)
        self.rules_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.rules_box.setLayout(rules_layout)

        # Labels and checkboxes
        self.lbl_pass_on_startup = QLabel()
        self.chk_pass_on_startup = QCheckBox()

        self.lbl_pass_on_product_update = QLabel()
        self.chk_pass_on_product_update = QCheckBox()

        self.lbl_pass_on_base_price_changed = QLabel()
        self.chk_pass_on_base_price_changed = QCheckBox()

        # NEW: sell price changed checkbox
        self.lbl_pass_on_sell_price_changed = QLabel()
        self.chk_pass_on_sell_price_changed = QCheckBox()

        self.lbl_pass_on_stock_adjustment = QLabel()
        self.chk_pass_on_stock_adjustment = QCheckBox()

        self.lbl_pass_on_new_stock = QLabel()
        self.chk_pass_on_new_stock = QCheckBox()

        # Add rows (label, checkbox)
        rules_layout.addRow(self.lbl_pass_on_startup, self.chk_pass_on_startup)
        rules_layout.addRow(self.lbl_pass_on_product_update, self.chk_pass_on_product_update)
        rules_layout.addRow(self.lbl_pass_on_base_price_changed, self.chk_pass_on_base_price_changed)
        rules_layout.addRow(self.lbl_pass_on_sell_price_changed, self.chk_pass_on_sell_price_changed)
        rules_layout.addRow(self.lbl_pass_on_stock_adjustment, self.chk_pass_on_stock_adjustment)
        rules_layout.addRow(self.lbl_pass_on_new_stock, self.chk_pass_on_new_stock)

        self.btn_save_rules = QPushButton()
        self.btn_save_rules.setFixedWidth(140)
        rules_btn_row = QHBoxLayout()
        rules_btn_row.addStretch(1)
        rules_btn_row.addWidget(self.btn_save_rules)

        self.right_col.addWidget(self.rules_box)
        self.right_col.addLayout(rules_btn_row)

        # SECURITY
        self.secr_box = QGroupBox()
        secr_layout = QFormLayout()
        self.secr_box.setLayout(secr_layout)

        self.lbl_old_pass = QLabel()
        self.txt_old_pass = QLineEdit()
        self.txt_old_pass.setEchoMode(QLineEdit.EchoMode.Password)

        self.lbl_new_pass = QLabel()
        self.txt_new_pass = QLineEdit()
        self.txt_new_pass.setEchoMode(QLineEdit.EchoMode.Password)

        self.lbl_confirm_pass = QLabel()
        self.txt_confirm_pass = QLineEdit()
        self.txt_confirm_pass.setEchoMode(QLineEdit.EchoMode.Password)

        secr_layout.addRow(self.lbl_old_pass, self.txt_old_pass)
        secr_layout.addRow(self.lbl_new_pass, self.txt_new_pass)
        secr_layout.addRow(self.lbl_confirm_pass, self.txt_confirm_pass)

        self.btn_save_pass = QPushButton()
        self.btn_save_pass.setFixedWidth(160)
        secr_btn_row = QHBoxLayout()
        secr_btn_row.addStretch(1)
        secr_btn_row.addWidget(self.btn_save_pass)

        self.right_col.addWidget(self.secr_box)
        self.right_col.addLayout(secr_btn_row)
        # Add expanding spacer so the right column doesn't compress the groupboxes and cut off text
        self.right_col.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

    def _connect_signals(self):
        self.btn_save_general.clicked.connect(self.save_general)
        self.btn_apply_lang.clicked.connect(self.apply_language_choice)
        self.btn_save_rules.clicked.connect(self.save_password_rules)
        self.btn_save_pass.clicked.connect(self.change_shopkeeper_password)

    def _apply_styles(self):

        self.setStyleSheet("""
            QFormLayout {
                background-color: white
            }
            QLineEdit {
                padding-top: 6px;
                padding-bottom: 6px;
                padding-left: 12px;
                padding-right: 12px;
                border-radius: 4px;
                border: 1px solid rgb(180,180,180);
            }
            QLineEdit:focus{
                border: 2px solid blue;

            }
            QCheckBox{
                margin-top: 10px
            }
            QGroupBox{
                border: 1px solid rgb(161, 161, 161);
                padding-top: 40px;
                background-color: white;
            }
            QGroupBox:Title{
                left: 25px;
                top: 2px;
                color: rgb(0, 0, 180);;
                padding-left: 4px;
                padding-right: 4px;
            }

        """)

    # ---------------- language manager hookup ----------------
    def _wire_language_manager(self):
        app = QApplication.instance()
        lm = getattr(app, "language_manager", None)
        if lm is not None:
            self._lang = lm.current
            lm.language_changed.connect(self.apply_language)
        else:
            try:
                kling = settings_service.get_setting("language")
                if kling:
                    self._lang = kling
            except Exception:
                self._lang = "ur"

    # ---------------- data load/save ----------------
    def load_settings(self):
        try:
            kv = settings_service.get_all_settings()
        except Exception:
            kv = {}

        # general
        self.txt_shop_name.setText(kv.get("shop_name", ""))
        self.txt_phone.setText(kv.get("shop_phone", ""))
        self.txt_address.setText(kv.get("shop_address", ""))

        # language
        lang = kv.get("language", self._lang)
        for i in range(self.cmb_lang.count()):
            if self.cmb_lang.itemData(i) == lang:
                self.cmb_lang.setCurrentIndex(i)
                break

        # password rules toggles stored as '0'/'1'
        def _bool_from(v):
            return str(v) == "1"

        self.chk_pass_on_startup.setChecked(_bool_from(kv.get("pass_on_startup", "0")))
        self.chk_pass_on_product_update.setChecked(_bool_from(kv.get("pass_on_product_update", "0")))
        self.chk_pass_on_base_price_changed.setChecked(_bool_from(kv.get("pass_on_base_price_changed", "0")))
        # new key
        self.chk_pass_on_sell_price_changed.setChecked(_bool_from(kv.get("pass_on_sell_price_changed", "0")))
        self.chk_pass_on_stock_adjustment.setChecked(_bool_from(kv.get("pass_on_stock_adjustment", "0")))
        self.chk_pass_on_new_stock.setChecked(_bool_from(kv.get("pass_on_new_stock", "0")))

    def save_general(self):
        shop_name = self.txt_shop_name.text().strip()
        phone = self.txt_phone.text().strip()
        address = self.txt_address.text().strip()
        try:
            # batch update using new helper to reduce DB hits
            settings_service.set_general({
                "shop_name": shop_name,
                "shop_phone": phone,
                "shop_address": address,
            })
            QMessageBox.information(self, "Saved", t("general_saved", self._lang))
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Failed to save settings:\n{exc}")

    def save_password_rules(self):
        try:
            # batch update using new helper to reduce DB hits
            settings_service.set_password_rules({
                "pass_on_startup": self.chk_pass_on_startup.isChecked(),
                "pass_on_product_update": self.chk_pass_on_product_update.isChecked(),
                "pass_on_base_price_changed": self.chk_pass_on_base_price_changed.isChecked(),
                "pass_on_sell_price_changed": self.chk_pass_on_sell_price_changed.isChecked(),  # new
                "pass_on_stock_adjustment": self.chk_pass_on_stock_adjustment.isChecked(),
                "pass_on_new_stock": self.chk_pass_on_new_stock.isChecked(),
            })
            QMessageBox.information(self, "Saved", t("general_saved", self._lang))
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Failed to save password rules:\n{exc}")

    def apply_language_choice(self):
        idx = self.cmb_lang.currentIndex()
        lang = self.cmb_lang.itemData(idx) if idx >= 0 else "ur"
        try:
            settings_service.set_setting("language", lang)
        except Exception:
            pass
        app = QApplication.instance()
        lm = getattr(app, "language_manager", None)
        if lm is not None and hasattr(lm, "set_language"):
            try:
                lm.set_language(lang)
            except Exception as exc:
                QMessageBox.critical(self, "Error", f"Failed to apply language:\n{exc}")
                return
        else:
            self.apply_language(lang)
        QMessageBox.information(self, "Language", t("language_applied", lang))

    def change_shopkeeper_password(self):
        old = self.txt_old_pass.text()
        new = self.txt_new_pass.text()
        conf = self.txt_confirm_pass.text()
        if not old or not new or not conf:
            QMessageBox.warning(self, "Validation", t("password_fill", self._lang))
            return
        if new != conf:
            QMessageBox.warning(self, "Validation", t("password_mismatch", self._lang))
            return
        if len(new) < 4:
            QMessageBox.warning(self, "Validation", t("password_short", self._lang))
            return
        try:
            shopkeeper_username = settings_service.get_setting("shopkeeper_username") or "admin"
        except Exception:
            shopkeeper_username = "admin"
        try:
            ok = user_service.change_password(shopkeeper_username, old, new)
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"{t('password_change_failed', self._lang)}\n{exc}")
            return
        if ok:
            QMessageBox.information(self, "Success", t("password_changed", self._lang))
            self.txt_old_pass.clear()
            self.txt_new_pass.clear()
            self.txt_confirm_pass.clear()
        else:
            QMessageBox.warning(self, "Failed", t("password_incorrect", self._lang))

    # ---------------- translations ----------------
    def apply_language(self, lang: str):
        if not lang:
            lang = "ur"
        self._lang = lang

        # general
        self.general_box.setTitle(t("general", lang))
        self.lbl_shop_name.setText(t("shop_name", lang))
        self.lbl_phone.setText(t("phone", lang))
        self.lbl_address.setText(t("address", lang))
        self.btn_save_general.setText(t("save", lang))

        # language
        self.lang_box.setTitle(t("language", lang))
        self.lbl_lang.setText(t("select_language", lang))
        self.btn_apply_lang.setText(t("apply", lang))

        # password rules labels
        self.rules_box.setTitle(t("password_rules_title", lang) if t("password_rules_title", lang) != "password_rules_title" else t("password_rules", lang))
        self.lbl_pass_on_startup.setText(t("ask_pass_startup", lang) or "Ask password on startup")
        self.lbl_pass_on_product_update.setText(t("ask_pass_on_product_update", lang) or "Ask password on product update")
        self.lbl_pass_on_base_price_changed.setText(t("ask_pass_on_base_price_changed", lang) or "Ask password if base price changed")
        # new label translation
        self.lbl_pass_on_sell_price_changed.setText(t("ask_pass_on_sell_price_changed", lang) or "Ask password if sell price changed")
        self.lbl_pass_on_stock_adjustment.setText(t("ask_pass_on_stock_adjustment", lang) or "Ask password on stock readjustment")
        self.lbl_pass_on_new_stock.setText(t("ask_pass_on_new_stock", lang) or "Ask password on new stock receipt")
        self.btn_save_rules.setText(t("save", lang))

        # security
        self.secr_box.setTitle(t("security", lang))
        self.lbl_old_pass.setText(t("old_password", lang))
        self.lbl_new_pass.setText(t("new_password", lang))
        self.lbl_confirm_pass.setText(t("confirm_password", lang))
        self.btn_save_pass.setText(t("change_password", lang))

        # placeholders
        self.txt_shop_name.setPlaceholderText(t("shop_name_ph", lang))
        self.txt_phone.setPlaceholderText(t("phone_ph", lang))
        self.txt_address.setPlaceholderText(t("address_ph", lang))
        self.txt_old_pass.setPlaceholderText(t("old_password_ph", lang))
        self.txt_new_pass.setPlaceholderText(t("new_password_ph", lang))
        self.txt_confirm_pass.setPlaceholderText(t("confirm_password_ph", lang))

        # layout direction
        if lang == "en":
            self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        else:
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        # localize combo display
        for i in range(self.cmb_lang.count()):
            code = self.cmb_lang.itemData(i)
            if code == "ur":
                self.cmb_lang.setItemText(i, "اردو" if lang == "ur" else "Urdu")
            elif code == "en":
                self.cmb_lang.setItemText(i, "English" if lang == "en" else "English")
