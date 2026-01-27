# app/screens/add_update_item.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QCheckBox, QDoubleSpinBox,
    QMessageBox, QInputDialog, QSizePolicy, QApplication
)
from PyQt6.QtCore import Qt
from decimal import Decimal
from datetime import datetime, timezone
import traceback

# translator: t(key, lang)
from utils.add_update_screen_tr import t as screen_t

# services (expected to exist)
try:
    from services import product_service
except Exception:
    product_service = None

try:
    from services import category_service
except Exception:
    category_service = None


class AddUpdateItem(QWidget):
    """
    Add / Update Item form. Use load_product(product_id) to switch to edit mode.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self._editing_id = None  # product id when editing, None for create

        self._build_ui()
        self._connect_signals()

        # subscribe to language changes
        app = QApplication.instance()
        lm = getattr(app, "language_manager", None)
        if lm is not None:
            lm.language_changed.connect(self.apply_language)
            # initial apply with current language
            self.apply_language(lm.current)
        else:
            self.apply_language("ur")

    # ---------------- UI ----------------
    def _build_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(12, 12, 12, 12)
        self.main_layout.setSpacing(12)

        # Title label
        self.lbl_title = QLabel("")
        font = self.lbl_title.font()
        font.setPointSize(font.pointSize() + 4)
        font.setBold(True)
        self.lbl_title.setFont(font)
        self.main_layout.addWidget(self.lbl_title)

        # Forms: left / middle / right
        self.left_form = QFormLayout()
        self.middle_form = QFormLayout()
        self.right_form = QFormLayout()

        # Create label widgets (so apply_language can update them)
        # LEFT
        self.lbl_barcode = QLabel()
        self.inp_barcode = QLineEdit()
        self.lbl_short_code = QLabel()
        self.inp_short_code = QLineEdit()
        self.lbl_item_name_ur = QLabel()
        self.inp_item_name_ur = QLineEdit()
        self.lbl_item_name_en = QLabel()
        self.inp_item_name_en = QLineEdit()

        # MIDDLE
        self.lbl_category = QLabel()
        self.cmb_category = QComboBox()
        self.btn_add_category = QPushButton("+")
        # make button width fixed and height match combo size hint
        self.btn_add_category.setFixedWidth(30)
        # set a reasonable fixed height (match typical combo height)
        self.btn_add_category.setFixedHeight(self.cmb_category.sizeHint().height() or 24)
        self.lbl_company = QLabel()
        self.inp_company = QLineEdit()
        self.lbl_unit = QLabel()
        self.cmb_unit = QComboBox()
        for u in ("kg", "pcs", "ltr", "box"):
            self.cmb_unit.addItem(u)

        # RIGHT
        self.lbl_base_price = QLabel()
        self.inp_base_price = QDoubleSpinBox()
        self.inp_base_price.setMaximum(9_999_999.99)
        self.inp_base_price.setDecimals(2)

        self.lbl_sell_price = QLabel()
        self.inp_sell_price = QDoubleSpinBox()
        self.inp_sell_price.setMaximum(9_999_999.99)
        self.inp_sell_price.setDecimals(2)

        self.lbl_initial_stock = QLabel()
        self.inp_initial_stock = QDoubleSpinBox()
        self.inp_initial_stock.setMaximum(9_999_999.999)
        self.inp_initial_stock.setDecimals(3)

        # packing
        self.chk_custom_packing = QCheckBox()
        self.lbl_packing_size = QLabel()
        self.inp_packing_size = QDoubleSpinBox()
        self.inp_packing_size.setMaximum(9_999_999.999)
        self.inp_packing_size.setDecimals(3)
        self.lbl_supply_pack_qty = QLabel()
        self.inp_supply_pack_qty = QDoubleSpinBox()
        self.inp_supply_pack_qty.setMaximum(9_999_999.999)
        self.inp_supply_pack_qty.setDecimals(3)

        self.lbl_reorder = QLabel()
        self.inp_reorder = QDoubleSpinBox()
        self.inp_reorder.setMaximum(9_999_999.999)
        self.inp_reorder.setDecimals(3)

        # Action buttons
        self.btn_save = QPushButton()
        self.btn_cancel = QPushButton()

        # Layout assembly (3 columns)
        cols = QHBoxLayout()
        cols.setSpacing(18)

        # LEFT column
        left_widget = QWidget()
        left_v = QVBoxLayout(left_widget)
        left_v.setContentsMargins(0, 0, 0, 0)
        self.left_form.addRow(self.lbl_barcode, self.inp_barcode)
        self.left_form.addRow(self.lbl_short_code, self.inp_short_code)
        self.left_form.addRow(self.lbl_item_name_ur, self.inp_item_name_ur)
        self.left_form.addRow(self.lbl_item_name_en, self.inp_item_name_en)
        left_v.addLayout(self.left_form)
        cols.addWidget(left_widget, 3)

        # MIDDLE column
        middle_widget = QWidget()
        mid_v = QVBoxLayout(middle_widget)
        mid_v.setContentsMargins(0, 0, 0, 0)
        # category row (combo + + button)
        cat_row = QHBoxLayout()
        cat_row.setContentsMargins(0, 0, 0, 0)
        cat_row.setSpacing(6)
        cat_row.addWidget(self.cmb_category)
        cat_row.addWidget(self.btn_add_category)
        self.middle_form.addRow(self.lbl_category, cat_row)
        self.middle_form.addRow(self.lbl_company, self.inp_company)
        self.middle_form.addRow(self.lbl_unit, self.cmb_unit)
        mid_v.addLayout(self.middle_form)
        cols.addWidget(middle_widget, 3)

        # RIGHT column
        right_widget = QWidget()
        right_v = QVBoxLayout(right_widget)
        right_v.setContentsMargins(0, 0, 0, 0)
        self.right_form.addRow(self.lbl_base_price, self.inp_base_price)
        self.right_form.addRow(self.lbl_sell_price, self.inp_sell_price)
        self.right_form.addRow(self.lbl_initial_stock, self.inp_initial_stock)

        # packing row: checkbox + packing size
        packing_row = QHBoxLayout()
        packing_row.setSpacing(8)
        packing_row.addWidget(self.chk_custom_packing)
        packing_row.addWidget(self.lbl_packing_size)
        packing_row.addWidget(self.inp_packing_size)
        packing_row.addWidget(self.lbl_supply_pack_qty)
        packing_row.addWidget(self.inp_supply_pack_qty)
        self.right_form.addRow(QLabel(""), packing_row)

        self.right_form.addRow(self.lbl_reorder, self.inp_reorder)
        right_v.addLayout(self.right_form)
        cols.addWidget(right_widget, 4)

        # actions row
        actions = QHBoxLayout()
        actions.addStretch(1)
        actions.addWidget(self.btn_save)
        actions.addWidget(self.btn_cancel)

        # Add to main layout
        self.main_layout.addLayout(cols)
        self.main_layout.addLayout(actions)

        # set placeholder texts (will be updated by apply_language)
        self.inp_barcode.setPlaceholderText("barcode")
        self.inp_short_code.setPlaceholderText("short_code")
        self.inp_item_name_ur.setPlaceholderText("item_name_ur")
        self.inp_item_name_en.setPlaceholderText("item_name_en")
        self.inp_company.setPlaceholderText("company")

        # load categories (service)
        self._reload_categories()

        # packing initial state
        self.inp_packing_size.setEnabled(False)
        # supply pack qty remains enabled always (independent)
        self.inp_supply_pack_qty.setEnabled(True)

        # default button texts
        self.btn_save.setText("Save")
        self.btn_cancel.setText("Cancel")

    # ---------------- signals ----------------
    def _connect_signals(self):
        self.btn_add_category.clicked.connect(self._on_add_category)
        self.btn_save.clicked.connect(self._on_save)
        self.btn_cancel.clicked.connect(self._on_cancel)
        self.chk_custom_packing.stateChanged.connect(self._on_toggle_packing)

    # ---------------- categories ----------------
    def _reload_categories(self):
        self.cmb_category.clear()
        try:
            if category_service:
                cats = category_service.list_categories(limit=500, offset=0)
                for c in cats:
                    name = c.get("name") or c.get("title") or str(c.get("id"))
                    self.cmb_category.addItem(name, c.get("id"))
            else:
                # no service — show placeholder only
                self.cmb_category.addItem("---", None)
        except Exception as exc:
            # fail gracefully
            self.cmb_category.addItem("---", None)

    def _on_add_category(self):
        # small dialog to create category
        name, ok = QInputDialog.getText(self, screen_t("category", self._current_lang()), screen_t("category", self._current_lang()))
        if not ok:
            return
        name = name.strip()
        if not name:
            QMessageBox.warning(self, screen_t("category", self._current_lang()), screen_t("category", self._current_lang()) + " is required.")
            return

        if not category_service or not hasattr(category_service, "create_category"):
            QMessageBox.critical(self, "Error", "Category service not available.")
            return

        try:
            created_id = category_service.create_category(name)
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Failed to create category:\n{str(exc)}")
            return

        # reload and select created
        self._reload_categories()
        # select the new id if present
        idx = next((i for i in range(self.cmb_category.count()) if self.cmb_category.itemData(i) == created_id), None)
        if idx is not None:
            self.cmb_category.setCurrentIndex(idx)

    # ---------------- packing toggle ----------------
    def _on_toggle_packing(self, state):
        enabled = bool(state)
        self.inp_packing_size.setEnabled(enabled)
        # supply_pack_qty stays enabled always (independent)

    # ---------------- create / update ----------------
    def _validate(self):
        if not (self.inp_item_name_ur.text().strip() or self.inp_item_name_en.text().strip()):
            return False, "Provide at least one name (Urdu or English)."
        # further validation can be added (unique barcode/short_code) by service
        return True, ""

    def _collect_data(self):
        cat_id = self.cmb_category.currentData()
        return {
            "short_code": self.inp_short_code.text().strip() or None,
            "ur_name": self.inp_item_name_ur.text().strip() or None,
            "en_name": self.inp_item_name_en.text().strip() or None,
            "company": self.inp_company.text().strip() or None,
            "barcode": self.inp_barcode.text().strip() or None,
            "base_price": Decimal(str(self.inp_base_price.value())),
            "sell_price": Decimal(str(self.inp_sell_price.value())),
            "stock_qty": Decimal(str(self.inp_initial_stock.value())),
            "reorder_threshold": Decimal(str(self.inp_reorder.value())),
            "category_id": int(cat_id) if cat_id else None,
            "unit": self.cmb_unit.currentText() or None,
            "custom_packing": 1 if self.chk_custom_packing.isChecked() else 0,
            "packing_size": Decimal(str(self.inp_packing_size.value())) if self.chk_custom_packing.isChecked() else None,
            "supply_pack_qty": Decimal(str(self.inp_supply_pack_qty.value())) if self.inp_supply_pack_qty.value() else None,
        }

    def _on_save(self):
        ok, msg = self._validate()
        if not ok:
            QMessageBox.warning(self, "Validation", msg)
            return

        data = self._collect_data()

        if not product_service or not hasattr(product_service, "create_product"):
            QMessageBox.critical(self, "Error", "Product service not available. Cannot save.")
            return

        try:
            if self._editing_id:
                # update mode
                success = product_service.update_product(self._editing_id, data)
                if success:
                    QMessageBox.information(self, "Success", f"Product (id={self._editing_id}) updated.")
                    self._clear_form()
                    # switch out of edit mode
                    self._editing_id = None
                    self._update_button_text()
                else:
                    QMessageBox.warning(self, "Warning", "Update reported failure.")
            else:
                # create mode
                new_id = product_service.create_product(data)
                QMessageBox.information(self, "Success", f"Product created (id={new_id}).")
                self._clear_form()
        except Exception as exc:
            trace = traceback.format_exc(limit=1)
            QMessageBox.critical(self, "Error", f"Failed to save product:\n{str(exc)}\n{trace}")

    def _on_cancel(self):
        self._clear_form()
        self._editing_id = None
        self._update_button_text()

    def _clear_form(self):
        self.inp_barcode.clear()
        self.inp_short_code.clear()
        self.inp_item_name_ur.clear()
        self.inp_item_name_en.clear()
        self.inp_company.clear()
        self.inp_base_price.setValue(0)
        self.inp_sell_price.setValue(0)
        self.inp_initial_stock.setValue(0)
        self.inp_packing_size.setValue(0)
        self.inp_supply_pack_qty.setValue(0)
        self.inp_reorder.setValue(0)
        self.chk_custom_packing.setChecked(False)
        if self.cmb_category.count():
            self.cmb_category.setCurrentIndex(0)

    # ---------------- load existing ----------------
    def load_product(self, product_id: int):
        """
        Load product into form for editing. Uses product_service.get_product().
        """
        if not product_service or not hasattr(product_service, "get_product"):
            QMessageBox.critical(self, "Error", "Product service not available. Cannot load item.")
            return

        prod = None
        try:
            prod = product_service.get_product(product_id)
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Failed to load product:\n{str(exc)}")
            return

        if not prod:
            QMessageBox.warning(self, "Not found", f"Product id={product_id} not found.")
            return

        # populate
        self._editing_id = prod["id"]
        self.inp_barcode.setText(prod.get("barcode") or "")
        self.inp_short_code.setText(prod.get("short_code") or "")
        self.inp_item_name_ur.setText(prod.get("ur_name") or "")
        self.inp_item_name_en.setText(prod.get("en_name") or "")
        self.inp_company.setText(prod.get("company") or "")
        self.inp_base_price.setValue(float(prod.get("base_price") or 0))
        self.inp_sell_price.setValue(float(prod.get("sell_price") or 0))
        self.inp_initial_stock.setValue(float(prod.get("stock_qty") or 0))
        self.inp_reorder.setValue(float(prod.get("reorder_threshold") or 0))
        self.chk_custom_packing.setChecked(bool(prod.get("custom_packing")))
        if prod.get("packing_size") is not None:
            self.inp_packing_size.setValue(float(prod.get("packing_size")))
        if prod.get("supply_pack_qty") is not None:
            self.inp_supply_pack_qty.setValue(float(prod.get("supply_pack_qty")))
        # select category if present, otherwise keep current
        cat_id = prod.get("category_id")
        if cat_id is not None:
            # reload categories to ensure list contains the id
            self._reload_categories()
            idx = next((i for i in range(self.cmb_category.count()) if self.cmb_category.itemData(i) == cat_id), None)
            if idx is not None:
                self.cmb_category.setCurrentIndex(idx)
        # update button label
        self._update_button_text()

    def _update_button_text(self):
        app_lang = self._current_lang()
        if self._editing_id:
            # No translator key for update provided — fallback to "Update"
            self.btn_save.setText("Update" if app_lang == "en" else "اپ ڈیٹ")
            self.lbl_title.setText("Update Item" if app_lang == "en" else "آئٹم میں تبدیلی کریں")
        else:
            self.btn_save.setText(screen_t("title", app_lang) or "Save")
            self.lbl_title.setText(screen_t("title", app_lang) or "")

    # --------------- language ----------------
    def _current_lang(self):
        app = QApplication.instance()
        lm = getattr(app, "language_manager", None)
        return getattr(lm, "current", "ur")

    def apply_language(self, lang: str):
        # set label texts
        try:
            self.lbl_barcode.setText(screen_t("barcode", lang))
            self.lbl_short_code.setText(screen_t("short_code", lang))
            self.lbl_item_name_ur.setText(screen_t("item_name_ur", lang))
            self.lbl_item_name_en.setText(screen_t("item_name_en", lang))
            self.lbl_category.setText(screen_t("category", lang))
            self.lbl_company.setText(screen_t("company", lang))
            self.lbl_unit.setText(screen_t("unit", lang))
            self.lbl_base_price.setText(screen_t("base_price", lang))
            self.lbl_sell_price.setText(screen_t("sell_price", lang))
            self.lbl_initial_stock.setText(screen_t("initial_stock", lang))
            self.lbl_packing_size.setText(screen_t("packing_size", lang))
            self.lbl_supply_pack_qty.setText(screen_t("supply_pack_qty", lang))
            self.lbl_reorder.setText(screen_t("reorder_threshold", lang))
        except Exception:
            pass

        # placeholders
        try:
            self.inp_barcode.setPlaceholderText(screen_t("barcode", lang))
            self.inp_short_code.setPlaceholderText(screen_t("short_code", lang))
            self.inp_item_name_ur.setPlaceholderText(screen_t("item_name_ur", lang))
            self.inp_item_name_en.setPlaceholderText(screen_t("item_name_en", lang))
            self.inp_company.setPlaceholderText(screen_t("company", lang))
        except Exception:
            pass

        # title and button labels
        self._update_button_text()

        # layout direction
        if lang == "en":
            self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        else:
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
