# app/screens/add_update_item.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QCheckBox, QDoubleSpinBox,
    QMessageBox, QInputDialog, QSizePolicy, QApplication, QFrame,
    QSpacerItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDoubleValidator, QCursor
from decimal import Decimal
from datetime import datetime, timezone
import traceback

# Modules
from utils.add_update_screen_tr import t
from services import product_service, category_service, settings_service
from app.modals.confirm_password_dialog import ConfirmPasswordDialog


class AddUpdateItem(QWidget):
    item_added_updated = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.loaded_product = None
        self.is_udpating = False
        self.active_input=''
        self.units_list = ["kg", 'gm', "ltr", "ml", "pcs"]
        self.init_ui()
        
        
        app = QApplication.instance()
        lm = getattr(app, "language_manager", None)
        if lm is not None:
            lm.language_changed.connect(self.apply_language)
            # initial apply with current language
            self.apply_language(lm.current)
        else:
            self.apply_language("ur")
            

    def init_ui(self):
        self.setMinimumSize(400, 500)
        self._create_components()       
        self._design_layout()
        self._apply_styles()
        
        
        # controls
        self._connect_buttons()
        self._reload_categories()
    
    def _create_components(self):
        self._double_validator()
        # Main layout
        self.main_layout = QVBoxLayout()
        
        self.form_layout = QHBoxLayout()
        self.right_side = QFrame()
        self.left_side = QFrame()
        self.right_form = QFormLayout()
        self.left_form = QFormLayout()
        self.button_layout = QHBoxLayout()
        self.category_layout = QHBoxLayout()
        
        # lables
        self.lbl_title = QLabel()
        self.lbl_barcode = QLabel()
        self.lbl_short_code = QLabel()
        self.lbl_item_name_ur = QLabel()
        self.lbl_item_name_en = QLabel()
        self.lbl_category = QLabel()
        self.lbl_company = QLabel()
        self.lbl_unit = QLabel()
        self.lbl_base_price = QLabel()
        self.lbl_sell_price = QLabel()
        self.lbl_initial_stock = QLabel()
        self.lbl_packing_size = QLabel()
        self.lbl_custom_pack = QLabel()
        self.lbl_supply_pack_size = QLabel()
        self.lbl_reorder = QLabel()
        
        # QlineEdit Inputs or ComboBox
        self.txt_barcode = QLineEdit()
        self.txt_short_code = QLineEdit()
        self.txt_item_name_ur = QLineEdit()
        self.txt_item_name_en = QLineEdit()
        self.cmb_category = QComboBox()
        self.txt_company = QLineEdit()
        self.cmb_unit = QComboBox()
        
        self.txt_base_price = QLineEdit()
        self.txt_sell_price = QLineEdit()
        self.txt_initial_stock = QLineEdit()
        self.txt_packing_size = QLineEdit()
        self.chk_custom_packing = QCheckBox()
        self.txt_supply_pack_size = QLineEdit()
        self.txt_reorder = QLineEdit()
        
        #buttons
        self.btn_save = QPushButton()
        self.btn_cancel = QPushButton()
        self.btn_category = QPushButton('+')
        self._apply_validator()
          
    # --------------- Design Layout ----------------
    def _design_layout(self):
        self.main_layout.addWidget(self.lbl_title, Qt.AlignmentFlag.AlignHCenter)
        
        #Right Form
        self.right_side.setLayout(self.right_form)
        self.right_form.addRow(self.lbl_barcode, self.txt_barcode)
        self.right_form.addRow(self.lbl_short_code, self.txt_short_code)
        self.right_form.addRow(self.lbl_item_name_ur, self.txt_item_name_ur)
        self.right_form.addRow(self.lbl_item_name_en, self.txt_item_name_en)
        
        #category 
        self.category_layout.addWidget(self.cmb_category)
        self.category_layout.addWidget(self.btn_category)
        self.cmb_category.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        self.right_form.addRow(self.lbl_category, self.category_layout)
        self.right_form.addRow(self.lbl_company, self.txt_company)
        check_layout = QHBoxLayout()
        check_layout.addWidget(self.txt_reorder)
        check_layout.addSpacerItem(QSpacerItem(10, 10))
        check_layout.addWidget(self.lbl_custom_pack)
        check_layout.addWidget(self.chk_custom_packing)
        self.right_form.addRow(self.lbl_reorder, check_layout)
        
        # Left Form
        self.left_side.setLayout(self.left_form)
        self.left_form.addRow(self.lbl_unit, self.cmb_unit)
        self.left_form.addRow(self.lbl_base_price, self.txt_base_price)
        self.left_form.addRow(self.lbl_sell_price, self.txt_sell_price)
        self.left_form.addRow(self.lbl_initial_stock, self.txt_initial_stock)
        
        self.left_form.addRow(self.lbl_packing_size, self.txt_packing_size)
        self.left_form.addRow(self.lbl_supply_pack_size, self.txt_supply_pack_size)

        #buttons and spacing
        self.button_layout.addSpacerItem(QSpacerItem(40, 40, hPolicy=QSizePolicy.Policy.Fixed, vPolicy=QSizePolicy.Policy.Expanding))
        self.button_layout.addWidget(self.btn_save, Qt.AlignmentFlag.AlignRight)
        self.button_layout.addSpacerItem(QSpacerItem(40, 40))
        self.button_layout.addWidget(self.btn_cancel, Qt.AlignmentFlag.AlignRight)
        self.button_layout.addSpacerItem(QSpacerItem(10, 10))

        self.left_form.addRow(self.button_layout)
        
        self.form_layout.addWidget(self.right_side)
        self.form_layout.addWidget(self.left_side)  
        self.main_layout.addLayout(self.form_layout)
     
        
        self.setLayout(self.main_layout)
        
    def _apply_styles(self):
        self.main_layout.setContentsMargins(30,30,30,30)
        # forms Spacing and Margins
        self.right_side.setContentsMargins(10, 10, 10, 10)
        self.right_form.setHorizontalSpacing(20)
        self.right_form.setVerticalSpacing(10)
        self.left_side.setContentsMargins(10, 10, 10, 10)
        self.left_form.setHorizontalSpacing(20)
        self.left_form.setVerticalSpacing(10)
        
        self.lbl_title.setFixedHeight(80)
        self.lbl_title.setObjectName('lblTitle')
        self.right_side.setObjectName('rightSide')
        self.left_side.setObjectName('leftSide')
        self.chk_custom_packing.setObjectName("chkCustomPack")

        self.btn_save.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_cancel.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_category.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_cancel.setObjectName("btnCancel")
        self.btn_save.setObjectName("btnSave")
        self.btn_category.setObjectName("btnCategory")
        self.setStyleSheet("""
        
            QLineEdit, QComboBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #007bff;
            }
            QLabel#lblTitle {
                font-size: 30px;
                font-weight: bold;
        
            }
            QCheckBox#chkCustomPack{
                padding: 10px
            }
            QPushButton#btnCancel,
            QPushButton#btnSave
            {
                padding: 6px 10px;
                border-radius: 4px;
                color: white;
                background-color: rgb(41, 132, 173);
                
            }
            #btnCategory{
                color: white;
                background-color: rgb(9, 122, 9);
                font-size: 20px;
                font-weight: 600;
            }
            QPushButton#btnCancel:hover,
            QPushButton#btnSave:hover {
                background-color: rgb(31, 100, 133);
            }
    
            QFrame#rightSide, QFrame#leftSide {
                border: 1px solid rgb(170, 170, 170);;
                border-radius: 4px;
                background-color: rgb(250, 250, 250);
            }
        """)
    
    # --------------- Validator ----------------
    def _double_validator(self):
        self.double_validator = QDoubleValidator(1.0, 999999999.0, 2, self)
        self.double_validator.setNotation(QDoubleValidator.Notation.StandardNotation)

    def _apply_validator(self):
        self.txt_base_price.setValidator(self.double_validator)
        self.txt_sell_price.setValidator(self.double_validator) 
        self.txt_initial_stock.setValidator(self.double_validator)
        self.txt_packing_size.setValidator(self.double_validator)
        self.txt_supply_pack_size.setValidator(self.double_validator)    
        self.txt_reorder.setValidator(self.double_validator)    
    
    def _connect_buttons(self):
        self.btn_category.clicked.connect(self._on_add_category)
        self.btn_save.clicked.connect(self._on_save)
        self.btn_cancel.clicked.connect(lambda: self._clear_form(True))
        
    # --------------- language ----------------
    def _current_lang(self):
        app = QApplication.instance()
        lm = getattr(app, "language_manager", None)
        return getattr(lm, "current", "ur")
        
    def apply_language(self, lang: str):
        # set label texts
        self._set_focus() # Setting Focus to barcode only
        try:
            self.lbl_title.setText(t("title", lang))
            self.lbl_barcode.setText(t("barcode", lang))
            self.lbl_short_code.setText(t("short_code", lang))
            self.lbl_item_name_ur.setText(t("item_name_ur", lang))
            self.lbl_item_name_en.setText(t("item_name_en", lang))
            self.lbl_category.setText(t("category", lang))
            self.lbl_company.setText(t("company", lang))
            self.lbl_unit.setText(t("unit", lang))
            self.lbl_base_price.setText(t("base_price", lang))
            self.lbl_sell_price.setText(t("sell_price", lang))
            self.lbl_initial_stock.setText(t("initial_stock", lang))
            self.lbl_packing_size.setText(t("packing_size", lang))
            self.lbl_supply_pack_size.setText(t("supply_pack_size", lang))
            self.lbl_custom_pack.setText(t("custom_packing", lang))
            self.lbl_reorder.setText(t("reorder_threshold", lang))
        except Exception:
            pass

        # placeholders
        try:
            self.txt_barcode.setPlaceholderText(t("barcode_ph", lang))
            self.txt_short_code.setPlaceholderText(t("short_code_ph", lang))
            self.txt_item_name_ur.setPlaceholderText(t("item_name_ur", lang))
            self.txt_item_name_en.setPlaceholderText(t("item_name_en", lang))
            self.txt_company.setPlaceholderText(t("company", lang))
        except Exception:
            pass

        # title and button labels
        self.btn_save.setText(t("save", lang))
        self.btn_cancel.setText(t("cancel", lang))
    
        
        # Combo box items
        self.cmb_unit.clear()
        for u in self.units_list:
            self.cmb_unit.addItem(t(u, lang), userData=u)
        # layout direction
        if lang == "en":
            self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        else:
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    
    # -------------- Controls ------------------------
    def _reload_categories(self):
        self.cmb_category.clear()
        try:
            if category_service:
                cats = category_service.list_categories(limit=500, offset=0)
                for c in cats:
                    name = c.get("name")
                    self.cmb_category.addItem(name, c.get("id"))
            else:
                # no service — show placeholder only
                self.cmb_category.addItem("---", None)
        except Exception as exc:
            # fail gracefully
            self.cmb_category.addItem("---", None)
    
    def _on_add_category(self):
        # small dialog to create category
        name, ok = QInputDialog.getText(self, t("category", self._current_lang()), t("category", self._current_lang()))
        if not ok:
            return
        name = name.strip()
        if not name:
            QMessageBox.warning(self, t("category", self._current_lang()), t("category", self._current_lang()) + " is required.")
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
            
    def _validate_input_data(self):
        lang = self._current_lang()
        if not self.txt_item_name_ur.text().strip():
            self.active_input = 'ur_name'
            return False, t('name_ur_error', lang), False
        elif not self.txt_reorder.text().strip():
            self.active_input = 'reorder'
            return False, t('reorder_error', lang), False
        elif not self.txt_base_price.text().strip():
            self.active_input = 'base_price'
            return False, t('base_price_error', lang), False
        elif not self.txt_sell_price.text().strip():
            self.active_input = 'sell_price'
            return False, t('sell_price_error', lang), False
        elif not self.txt_initial_stock.text().strip():
            self.active_input = 'initial_stock'
            return False, t('initial_stock_error', lang), False
        
        if Decimal(self.txt_base_price.text().strip()) >= Decimal(self.txt_sell_price.text().strip()):
            ret = QMessageBox.warning(
            self, 
            t("price_warning", lang), 
            t('price_warning_msg', lang),
            QMessageBox.StandardButton.Ignore | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel # Set Cancel as the default highlighted button
            )
            # 4. Check which button was clicked
            if ret == QMessageBox.StandardButton.Cancel:
                # Stop execution if they click Cancel
                self.active_input = 'sell_price'
                return False, "user_cancelled", True

        return True, "", False   

    def _collect_data(self):
        cat_id = self.cmb_category.currentData()
        unit_data = self.cmb_unit.currentData()
        
        return {
            "short_code": self.txt_short_code.text().strip() or None,
            "ur_name": self.txt_item_name_ur.text().strip() or None,
            "en_name": self.txt_item_name_en.text().strip() or None,
            "company": self.txt_company.text().strip() or None,
            "barcode": self.txt_barcode.text().strip() or None,
            "base_price": Decimal(self.txt_base_price.text()),
            "sell_price": Decimal(self.txt_sell_price.text()),
            "stock_qty": Decimal(self.txt_initial_stock.text()),
            "reorder_threshold": Decimal(self.txt_reorder.text()) ,
            "category_id": int(cat_id) if cat_id else None,
            "unit": unit_data,
            "custom_packing": 1 if self.chk_custom_packing.isChecked() else 0,
            "packing_size": Decimal(self.txt_packing_size.text()) if self.txt_packing_size.text() else None,
            "supply_pack_qty": Decimal(self.txt_supply_pack_size.text()) if self.txt_supply_pack_size.text() else None,
        }

    def _on_save(self):
        
        ok, msg, stop_only = self._validate_input_data()
        if not ok and  not stop_only:
            QMessageBox.warning(self, "Validation", msg)
            self._set_focus()
            return
        if stop_only:
            self._set_focus()
            return

        data = self._collect_data()
        
        if not product_service or not hasattr(product_service, "create_product"):
            QMessageBox.critical(self, "Error", "Product service not available. Cannot save.")
            return
        confirm_pass = self._confirm_password(data)
        if not confirm_pass:
            return
        try:
            if self.is_udpating:
                # update mode
                success = product_service.update_product(self.loaded_product.get('id', None), data)
                if success:
                    QMessageBox.information(self, "Success", f"Product (id={self._editing_id}) updated.")
                    self._clear_form()
                    # switch out of edit mode
                    self._editing_id = None

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
        
        self.item_added_updated.emit('addUpdate')
    
    def _clear_form(self, warning: bool = False):
        if warning:
            lang = self._current_lang()
            ret = QMessageBox.warning(
            self, 
            t("warning", lang), 
            t('clear_warning_msg', lang),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
            )
            # 4. Check which button was clicked
            if ret == QMessageBox.StandardButton.No:
                return
            
        self.txt_barcode.clear()
        self.txt_short_code.clear()
        self.txt_item_name_ur.clear()
        self.txt_item_name_en.clear()
        self.txt_company.clear()
        self.txt_base_price.clear()
        self.txt_sell_price.clear()
        self.txt_initial_stock.clear()
        self.txt_packing_size.clear()
        self.txt_supply_pack_size.clear()
        self.txt_reorder.clear()
        self.chk_custom_packing.setChecked(False)

        self.is_udpating = False
        self.txt_initial_stock.setDisabled(False)
        self.txt_barcode.setFocus()

    def _set_focus(self):
        tt = self.active_input
        if tt == '':
            self.txt_barcode.setFocus()
        elif tt == 'ur_name':
            self.txt_item_name_ur.setFocus()
        elif tt == 'reorder':
            self.txt_reorder.setFocus()
        elif tt == 'base_price':
            self.txt_base_price.setFocus()
        elif tt == 'sell_price':
            self.txt_sell_price.setFocus()
        elif tt == 'initial_stock':
            self.txt_initial_stock.setFocus()

    def load_product(self, id: int = -1):
        """
        Load product from service and populate fields.
        """
        self.is_udpating = True  # your existing flag (typo kept to avoid other changes)
        if id == -1:
            return

        self.loaded_product = product_service.get_product(id)

        self.txt_initial_stock.setDisabled(True)
        # keep a handy editing id for save/update logic
        self._editing_id = id
        # populate UI
        try:
            self._populate_fields()
        except Exception as exc:
            print("Error populating fields:", exc)
            # still allow editing if partial failure

    def _populate_fields(self):
        """
        Copy values from self.loaded_product to widgets.
        Converts None/Decimal to string-safe values, selects category and unit.
        """
        p = getattr(self, "loaded_product", None)
        if not p:
            return

        # simple helper to convert None/Decimal to string
        def s(val):
            if val is None:
                return ""
            # handle Decimal and other numeric types
            if isinstance(val, Decimal):
                # remove exponent if integer-like, otherwise show normalized
                try:
                    if val == val.to_integral():
                        return str(int(val))
                    return format(val.normalize(), 'f')
                except Exception:
                    return str(val)
            return str(val)

        # textual fields
        self.txt_barcode.setText(s(p.get("barcode")))
        self.txt_short_code.setText(s(p.get("short_code")))
        # language-specific name fields
        self.txt_item_name_en.setText(s(p.get("en_name")))
        self.txt_item_name_ur.setText(s(p.get("ur_name")))

        # company may be literal "None" — treat as empty
        company_val = p.get("company")
        if company_val is None or str(company_val).strip().lower() == "none":
            company_str = ""
        else:
            company_str = str(company_val)
        self.txt_company.setText(company_str)

        # numeric fields (use helper to format decimals)
        self.txt_base_price.setText(s(p.get("base_price")))
        self.txt_sell_price.setText(s(p.get("sell_price")))
        self.txt_initial_stock.setText(s(p.get("stock_qty")))
        self.txt_reorder.setText(s(p.get("reorder_threshold")))
        self.txt_packing_size.setText(s(p.get("packing_size")))
        self.txt_supply_pack_size.setText(s(p.get("supply_pack_qty")))

        # custom packing checkbox
        self.chk_custom_packing.setChecked(bool(p.get("custom_packing")))

        # select category by itemData (which you populated with category id)
        cat_id = p.get("category_id")
        if cat_id is not None and hasattr(self, "cmb_category"):
            found_idx = -1
            for i in range(self.cmb_category.count()):
                try:
                    if self.cmb_category.itemData(i) == cat_id:
                        found_idx = i
                        break
                except Exception:
                    # fallback comparing string values
                    if str(self.cmb_category.itemData(i)) == str(cat_id):
                        found_idx = i
                        break
            if found_idx >= 0:
                self.cmb_category.setCurrentIndex(found_idx)

        # select unit by matching item text or raw unit value
        unit_val = p.get("unit") or ""
        if unit_val:
            unit_val_norm = str(unit_val).strip().lower()
            found_u = -1
            for i in range(self.cmb_unit.count()):
                itm_text = str(self.cmb_unit.itemText(i)).strip().lower()
                if itm_text == unit_val_norm or itm_text.startswith(unit_val_norm):
                    found_u = i
                    break
            if found_u >= 0:
                self.cmb_unit.setCurrentIndex(found_u)

        # set focus to barcode (or maintain previous active input)
        self._set_focus()
    
    def _confirm_password(self, data: any = None) -> bool:
        """
        Return True if password confirmation not required or user confirmed correctly,
        otherwise return False.

        Rules checked (any -> require password):
        - pass_on_product_update  (always on update)
        - pass_on_base_price_changed (only if base_price changed)
        - pass_on_sell_price_changed (only if sell_price changed)
        """
        from decimal import Decimal, InvalidOperation

        st = settings_service.get_all_settings() or {}
        def _is_true(v) -> bool:
            try:
                return str(v).strip().lower() in ("1", "true", "yes")
            except Exception:
                return False

        # If this is not an update, we don't require confirmation here
        if not getattr(self, "is_udpating", False):
            return True

        # Determine whether any rule requires asking for password
        require_password = False

        # 1) global "ask on any product update"
        if _is_true(st.get("pass_on_product_update", "0")):
            require_password = True
        else:
            # If global update password not set, check specific change rules
            # Check base price change
            if _is_true(st.get("pass_on_base_price_changed", "0")):
                try:
                    new_base = data.get("base_price") if data else None
                    old_base = getattr(self, "loaded_product", {}).get("base_price") if getattr(self, "loaded_product", None) else None
                    if new_base is not None and old_base is not None:
                        new_d = Decimal(str(new_base))
                        old_d = Decimal(str(old_base))
                        if new_d != old_d:
                            require_password = True
                except (InvalidOperation, AttributeError, TypeError):
                    # If unable to compare, conservatively do not trigger here.
                    pass

            # Check sell price change (only if not already requiring)
            if not require_password and _is_true(st.get("pass_on_sell_price_changed", "0")):
                try:
                    new_sell = data.get("sell_price") if data else None
                    old_sell = getattr(self, "loaded_product", {}).get("sell_price") if getattr(self, "loaded_product", None) else None
                    if new_sell is not None and old_sell is not None:
                        new_d = Decimal(str(new_sell))
                        old_d = Decimal(str(old_sell))
                        if new_d != old_d:
                            require_password = True
                except (InvalidOperation, AttributeError, TypeError):
                    pass

        # If no rule requires password, allow action
        if not require_password:
            return True

        # Otherwise show the confirm dialog once
        try:
            dlg = ConfirmPasswordDialog(self, reason="Please confirm your password to continue", max_attempts=3)
            ok = dlg.exec_confirm()
            return bool(ok)
        except Exception as exc:
            # If dialog fails for any reason, fail-safe: deny the operation
            print("Confirm password dialog error:", exc)
            return False
