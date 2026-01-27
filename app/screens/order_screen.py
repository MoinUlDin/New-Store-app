# File: app/screens/order_screen.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, 
    QLineEdit, QComboBox, QPushButton, QTableWidget, 
    QHeaderView, QTableWidgetItem, QAbstractItemView
)
from PyQt6.QtCore import Qt
from utils.order_screen_tr import t  # Importing the screen-specific translator

class OrderScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(15)

        # UI Components that need translation updates
        self.cart_title = QLabel()
        self.search_label = QLabel()
        self.cat_label = QLabel()
        self.comp_label = QLabel()
        self.lbl_subtotal_text = QLabel()
        self.lbl_qty_text = QLabel()
        self.lbl_total_text = QLabel()
        self.btn_checkout = QPushButton()

        self._init_cart_panel()     # Left Side
        self._init_search_panel()   # Right Side

    def _init_cart_panel(self):
        """Builds the left side 'Tokri' area."""
        left_panel = QFrame()
        left_panel.setFixedWidth(350)
        left_panel.setObjectName("cartPanel")
        layout = QVBoxLayout(left_panel)

        # Title
        self.cart_title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(self.cart_title, alignment=Qt.AlignmentFlag.AlignRight)

        # Cart Table
        self.cart_table = QTableWidget(0, 4)
        self.cart_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.cart_table)

        # Totals Section
        totals_frame = QFrame()
        totals_layout = QVBoxLayout(totals_frame)
        
        self.lbl_subtotal_text.setStyleSheet("font-size: 16px;")
        self.lbl_qty_text.setStyleSheet("font-size: 16px;")
        self.lbl_total_text.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        totals_layout.addWidget(self.lbl_subtotal_text)
        totals_layout.addWidget(self.lbl_qty_text)
        totals_layout.addWidget(self.lbl_total_text)
        layout.addWidget(totals_frame)

        # Checkout Button
        self.btn_checkout.setFixedHeight(50)
        self.btn_checkout.setObjectName("checkoutButton") # Target this in QSS for green color
        layout.addWidget(self.btn_checkout)

        self.main_layout.addWidget(left_panel)

    def _init_search_panel(self):
        """Builds the right side search and selection area."""
        right_panel = QFrame()
        layout = QVBoxLayout(right_panel)

        # 1. Search Label and Bar
        self.search_label.setStyleSheet("font-size: 20px;")
        layout.addWidget(self.search_label, alignment=Qt.AlignmentFlag.AlignRight)

        search_bar_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setFixedHeight(40)
        search_bar_layout.addWidget(self.search_input)
        
        # Search Icon Button (The green magnifying glass)
        btn_search = QPushButton("🔍")
        btn_search.setFixedSize(40, 40)
        btn_search.setStyleSheet("background-color: #2e7d32; color: white;")
        search_bar_layout.addWidget(btn_search)
        layout.addLayout(search_bar_layout)

        # 2. Filters (Category / Company)
        filter_layout = QHBoxLayout()
        
        self.combo_category = QComboBox()
        self.combo_category.setFixedHeight(35)
        
        self.combo_company = QComboBox()
        self.combo_company.setFixedHeight(35)
        
        filter_layout.addWidget(self.combo_category)
        filter_layout.addWidget(self.combo_company)
        layout.addLayout(filter_layout)

        # 3. Product Selection Area (Placeholder for results)
        self.results_area = QFrame()
        self.results_area.setFrameShape(QFrame.Shape.StyledPanel)
        layout.addWidget(self.results_area, 1) # Takes up remaining space

        self.main_layout.addWidget(right_panel)

    def apply_language(self, lang: str):
        """Updates all strings on the screen and handles RTL/LTR direction."""
        # Update Titles & Labels
        self.cart_title.setText(t("tokri", lang))
        self.search_label.setText(t("search_item", lang))
        self.search_input.setPlaceholderText(t("search_placeholder", lang))
        
        # Update Totals
        self.lbl_subtotal_text.setText(f"{t('subtotal', lang)}: 0")
        self.lbl_qty_text.setText(f"{t('qty', lang)}: 0")
        self.lbl_total_text.setText(f"{t('total', lang)}: 0")
        self.btn_checkout.setText(t("checkout", lang))

        # Update Table Headers
        headers = [t("item", lang), t("price", lang), t("qty", lang), t("total", lang)]
        self.cart_table.setHorizontalHeaderLabels(headers)

        # Handle RTL/LTR specifically for this screen's container
        if lang == "ur":
            self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        else:
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)