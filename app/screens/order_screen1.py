# app/screens/order_screen.py
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QGroupBox,
    QFrame,
    QSizePolicy,
    QSpacerItem,
    QApplication,
)
from PyQt6.QtGui import QIcon, QPixmap, QFontDatabase, QFont
from PyQt6.QtCore import Qt, QSize
import os

from utils.order_screen_tr import t 


def resources_path(*parts) -> str:
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    return os.path.join(root, "resources", *parts)


class OrderScreen(QWidget):
    def __init__(self):
        super().__init__()

        # Build UI
        self.build_ui()
        self.apply_styles()

        # Connect to LanguageManager if available so runtime language changes apply here
        app = QApplication.instance()
        lm = getattr(app, "language_manager", None)
        if lm is not None:
            lm.language_changed.connect(self.apply_language)
            # initial apply using manager's current language
            self.apply_language(lm.current)
        else:
            # fallback to default 'ur'
            self.apply_language("ur")

    def build_ui(self):
        # Main horizontal layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(12)

        # Left: Cart (GroupBox visual)
        left_box = QGroupBox()
        left_box.setTitle("ٹوکری")
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(8, 40, 8, 8)
        left_layout.setSpacing(8)

        # Cart table
        self.cart_table = QTableWidget(0, 4)
        # We'll keep header labels dynamic via apply_language
        self.cart_table.setHorizontalHeaderLabels(["Item", "Price", "Qty", "Total"])
        self.cart_table.horizontalHeader().setStretchLastSection(True)
        self.cart_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        left_layout.addWidget(self.cart_table)

        # Summary area (small)
        summary_frame = QFrame()
        summary_layout = QVBoxLayout()
        summary_layout.setContentsMargins(0, 0, 0, 0)
        summary_layout.setSpacing(6)

        self.lbl_subtotal = QLabel("Subtotal: 0")
        self.lbl_qty = QLabel("Qty: 0")
        self.lbl_total = QLabel("Total: 0")

        summary_layout.addWidget(self.lbl_subtotal)
        summary_layout.addWidget(self.lbl_qty)
        summary_layout.addWidget(self.lbl_total)
        summary_frame.setLayout(summary_layout)

        left_layout.addWidget(summary_frame)

        # Checkout button (large green)
        self.btn_checkout = QPushButton("Checkout")
        self.btn_checkout.setMinimumHeight(46)
        self.btn_checkout.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        left_layout.addWidget(self.btn_checkout)

        left_box.setLayout(left_layout)
        left_box.setMinimumWidth(260)

        # Right: Add item area
        right_box = QGroupBox()
        right_box.setTitle("آئٹم شامل کریں")
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(20, 40, 20, 20)
        right_layout.setSpacing(10)

        # Search input with search icon at left (green border like screenshot)
        search_frame = QFrame()
        search_frame.setObjectName("searchFrame")
        search_h = QHBoxLayout()
        search_h.setContentsMargins(6, 6, 6, 6)
        search_h.setSpacing(6)

        # Search icon
        search_icon_path = resources_path("icons", "search.svg")
        search_lbl = QLabel()
        if os.path.exists(search_icon_path):
            pix = QPixmap(search_icon_path).scaled(26, 26, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            search_lbl.setPixmap(pix)
            search_lbl.setFixedWidth(40)
            search_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Search line edit
        self.txt_search = QLineEdit()
        # placeholder text applied in apply_language
        self.txt_search.setObjectName("bigSearch")
        self.txt_search.setMinimumHeight(44)

        search_h.addWidget(search_lbl)
        search_h.addWidget(self.txt_search)
        search_frame.setLayout(search_h)

        right_layout.addWidget(search_frame)

        # Dropdown placeholders: category & brand (use QLineEdit for now)
        cat_brand_layout = QHBoxLayout()
        self.txt_category = QLineEdit()
        self.txt_category.setMinimumHeight(40)
        self.txt_brand = QLineEdit()
        self.txt_brand.setMinimumHeight(40)
        cat_brand_layout.addWidget(self.txt_category)
        cat_brand_layout.addWidget(self.txt_brand)
        right_layout.addLayout(cat_brand_layout)

        # Item info table-like area (labels on right, values on left aligned)
        info_layout = QHBoxLayout()
        info_layout.setSpacing(10)

        # labels column (urdu on right)
        labels_col = QVBoxLayout()
        self.lbl_name = QLabel("آئٹم کا نام")
        self.lbl_company = QLabel("کمپنی")
        self.lbl_price = QLabel("قیمت")
        labels_col.addWidget(self.lbl_name)
        labels_col.addWidget(self.lbl_company)
        labels_col.addWidget(self.lbl_price)
        info_layout.addLayout(labels_col)

        # inputs column
        inputs_col = QVBoxLayout()
        self.txt_name = QLineEdit()
        self.txt_price = QLineEdit()
        self.txt_qty = QLineEdit()
        self.txt_name.setMinimumHeight(36)
        self.txt_price.setMinimumHeight(36)
        self.txt_qty.setMinimumHeight(36)
        inputs_col.addWidget(self.txt_name)
        inputs_col.addWidget(self.txt_price)
        inputs_col.addWidget(self.txt_qty)
        info_layout.addLayout(inputs_col)

        right_layout.addLayout(info_layout)

        # Add button
        self.btn_add = QPushButton("Add")
        self.btn_add.setMinimumHeight(40)
        right_layout.addWidget(self.btn_add)

        # spacer to push content up
        right_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        right_box.setLayout(right_layout)
        right_box.setMinimumWidth(700)

        # Add left and right to main (match screenshot: right main area, left cart)
        main_layout.addWidget(right_box, 5)
        main_layout.addWidget(left_box, 2)

        # Save references
        self.left_box = left_box
        self.right_box = right_box

    def apply_styles(self):
        # Stylesheet approximating the card-like UI from screenshot
        self.setStyleSheet("""
        QGroupBox {
            border: 1px solid #e0e6e6;
            border-radius: 8px;
            background: #fbfdfe;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px 0 3px;
            font-weight: bold;
        }
        #searchFrame {
            border: 2px solid #1aa261; /* green border */
            border-radius: 6px;
            background: white;
        }
        #bigSearch {
            border: none;
            font-size: 16px;
        }
        QPushButton {
            border-radius: 6px;
            padding: 6px 12px;
        }
        QPushButton#checkout {
            background: #2f9b58;
            color: white;
            font-weight: bold;
        }
        QPushButton#add {
            background: #2f9b58;
            color: white;
            width: 120px;
        }
        QLabel#bigHeader {
            font-size: 20px;
            font-weight: 600;
        }
        """)
        # mark specific widgets
        self.btn_checkout.setObjectName("checkout")
        self.btn_add.setObjectName("add")

    def apply_language(self, lang: str):
        """
        Apply layout direction and update visible strings/placeholders.
        This relies on t(key) translator which reads the global language (set by LanguageManager).
        If t() is missing a key or not present, fall back to hardcoded Urdu/English literals.
        """
        # Layout direction
        if lang == "en":
            self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        else:
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        # Update placeholders and labels using i18n
        self.txt_search.setPlaceholderText(t("placeholder_search") or 'wowowwo')
        try:
            pass
        except Exception:
            # fallback Urdu literal
            self.txt_search.setPlaceholderText("بارکوڈ اسکین کریں یا نام لکھیں...")

        try:
            self.txt_category.setPlaceholderText(t("placeholder_company"))
        except Exception:
            self.txt_category.setPlaceholderText("کمپنی منتخب کریں")

        try:
            self.txt_brand.setPlaceholderText(t("placeholder_category"))
        except Exception:
            self.txt_brand.setPlaceholderText("زمرہ منتخب کریں")

        try:
            self.lbl_name.setText(t("item_name_label"))
        except Exception:
            self.lbl_name.setText("آئٹم کا نام")

        try:
            self.lbl_company.setText(t("company_label"))
        except Exception:
            self.lbl_company.setText("کمپنی")

        try:
            self.lbl_price.setText(t("price_label"))
        except Exception:
            self.lbl_price.setText("قیمت")

        try:
            self.txt_name.setPlaceholderText(t("placeholder_item_name"))
        except Exception:
            self.txt_name.setPlaceholderText("آئٹم کا نام")

        try:
            self.txt_price.setPlaceholderText(t("placeholder_price"))
        except Exception:
            self.txt_price.setPlaceholderText("قیمت")

        try:
            self.txt_qty.setPlaceholderText(t("placeholder_qty"))
        except Exception:
            self.txt_qty.setPlaceholderText("مقدار")

        # Update cart header & summary labels
        try:
            self.left_box.setTitle(t("cart_title"))
        except Exception:
            self.left_box.setTitle("ٹوکری / Cart")

        try:
            self.right_box.setTitle(t("add_item_title"))
        except Exception:
            self.right_box.setTitle("آئٹم شامل کریں")

        # Update buttons
        try:
            self.btn_checkout.setText(t("checkout_button"))
        except Exception:
            self.btn_checkout.setText("Checkout")

        try:
            self.btn_add.setText(t("add_button"))
        except Exception:
            self.btn_add.setText("Add")

        # Update cart table headers
        try:
            headers = [
                t("cart_col_item"),
                t("cart_col_price"),
                t("cart_col_qty"),
                t("cart_col_total"),
            ]
            self.cart_table.setHorizontalHeaderLabels(headers)
        except Exception:
            self.cart_table.setHorizontalHeaderLabels(["Item", "Price", "Qty", "Total"])
