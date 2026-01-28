# app/screens/add_update_item.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QCheckBox, QDoubleSpinBox,
    QMessageBox, QInputDialog, QSizePolicy, QApplication, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator
from decimal import Decimal
from datetime import datetime, timezone
import traceback
from utils.add_update_screen_tr import t


class AddUpdateItem(QWidget):
    def __init__(self, parent=None, item=None):
        super().__init__(parent)
        self.parent = parent
        self.item = item
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
        self.setMinimumSize(400, 300)
        self._create_components()       
        self._design_layout()
        self._apply_styles()
    
    def _create_components(self):
        self._init_validator()
        # Main layout
        self.main_layout = QVBoxLayout()
        
        self.form_layout = QHBoxLayout()
        self.right_side = QFrame()
        self.left_side = QFrame()
        self.right_form = QFormLayout()
        self.left_form = QFormLayout()
        self.button_layout = QHBoxLayout()
        
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
        self.lbl_supply_pack_qty = QLabel()
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
        self.txt_supply_pack_qty = QLineEdit()
        self.txt_reorder = QLineEdit()
        
        self.btn_save = QPushButton()
        self.btn_cancel = QPushButton()
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
        self.right_form.addRow(self.lbl_category, self.cmb_category)
        self.right_form.addRow(self.lbl_company, self.txt_company)
        
        # Left Form
        self.left_side.setLayout(self.left_form)
        self.left_form.addRow(self.lbl_unit, self.cmb_unit)
        self.left_form.addRow(self.lbl_base_price, self.txt_base_price)
        self.left_form.addRow(self.lbl_sell_price, self.txt_sell_price)
        self.left_form.addRow(self.lbl_initial_stock, self.txt_initial_stock)
        self.left_form.addRow(self.lbl_packing_size, self.txt_packing_size)
        self.left_form.addRow(self.lbl_supply_pack_qty, self.txt_supply_pack_qty)

        self.button_layout.addWidget(self.btn_save, Qt.AlignmentFlag.AlignRight)
        self.button_layout.addWidget(self.btn_cancel, Qt.AlignmentFlag.AlignRight)
        
        self.form_layout.addWidget(self.right_side)
        self.form_layout.addWidget(self.left_side)  
        self.main_layout.addLayout(self.form_layout)
        self.main_layout.addLayout(self.button_layout)  
        
        self.setLayout(self.main_layout)
        
    def _apply_styles(self):
        self.main_layout.setContentsMargins(30,30,30,30)
        self.lbl_title.setFixedHeight(80)
        self.lbl_title.setObjectName('lblTitle')
        self.right_side.setObjectName('rightSide')
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
            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
                background-color: #007bff;
            }
            QFrame#rightSide {
                border: 1px solid black;
                border-radius: 4px;
            }
        """)
    # --------------- Validator ----------------
    def _init_validator(self):
        self.double_validator = QDoubleValidator(0.0, 1000.0, 2, self)
        self.double_validator.setNotation(QDoubleValidator.Notation.StandardNotation)

    def _apply_validator(self):
        self.txt_base_price.setValidator(self.double_validator)
        self.txt_sell_price.setValidator(self.double_validator) 
        self.txt_initial_stock.setValidator(self.double_validator)
        self.txt_packing_size.setValidator(self.double_validator)
        self.txt_supply_pack_qty.setValidator(self.double_validator)    
        
    # --------------- language ----------------
    def _current_lang(self):
        app = QApplication.instance()
        lm = getattr(app, "language_manager", None)
        return getattr(lm, "current", "ur")
        
    def apply_language(self, lang: str):
        # set label texts
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
            self.lbl_supply_pack_qty.setText(t("supply_pack_qty", lang))
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
            self.cmb_unit.addItem(t(u, lang))

        # layout direction
        if lang == "en":
            self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        else:
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    