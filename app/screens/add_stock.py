# app/screens/add_stock.py

from typing import List, Dict, Any, Optional
from decimal import Decimal, InvalidOperation

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QSpinBox,
    QDoubleSpinBox, QSizePolicy, QFrame, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from services import product_service, stock_service
from services.user_service import get_current_user
from services.settings_service import get_setting
from data.db import get_connection
from utils.add_stock_tr import t


class AddStock(QWidget):
    """
    Screen to receive packs for existing products.

    Flow:
      - Search product by name / barcode / short_code
      - Select product from results
      - Enter num_packs, optional cost_total, optional reference id (text)
      - Preview current stock, added qty and new stock
      - Click "Receive" -> calls stock_service.receive_packs(...)

    Signals:
      stock_received() - emitted after successful receive (so other screens can refresh)
    """
    stock_received = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang = "ur"
        app = None
        try:
            from PyQt6.QtWidgets import QApplication
            app = QApplication.instance()
        except Exception:
            app = None
        lm = getattr(app, "language_manager", None) if app else None
        if lm is not None:
            self.lang = lm.current
            lm.language_changed.connect(self.apply_language)
        else:
            try:
                kling = get_setting("language")
                if kling:
                    self.lang = kling
            except Exception:
                self.lang = "ur"

        self._raw_results: List[Dict[str, Any]] = []
        self._selected_product: Optional[Dict[str, Any]] = None

        # labels we will need to update in apply_language
        self.lbl_unit_label: Optional[QLabel] = None
        self.lbl_supply_label: Optional[QLabel] = None
        self.lbl_current_label: Optional[QLabel] = None
        self.lbl_added_label: Optional[QLabel] = None
        self.lbl_new_label: Optional[QLabel] = None
        self.lbl_num_packs_label: Optional[QLabel] = None
        self.lbl_cost_label: Optional[QLabel] = None

        self._build_ui()
        self._connect_signals()
        self._apply_styles()

    # ---------------- UI ----------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        # Search row (compact modern controls)
        row_search = QHBoxLayout()
        row_search.setSpacing(8)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            t("search_products_placeholder", self.lang)
            if t("search_products_placeholder", self.lang) != "search_products_placeholder"
            else "Search by name, barcode or short code"
        )
        self.search_input.setFixedHeight(36)
        self.search_input.setObjectName("searchInput")

        self.btn_search = QPushButton(t("search", self.lang) if t("search", self.lang) != "search" else "Search")
        self.btn_search.setFixedHeight(36)
        self.btn_search.setObjectName("primaryBtn")

        self.btn_refresh = QPushButton(t("refresh", self.lang) if t("refresh", self.lang) != "refresh" else "Refresh")
        self.btn_refresh.setFixedHeight(36)
        self.btn_refresh.setObjectName("secondaryBtn")

        row_search.addWidget(self.search_input, 5)
        row_search.addWidget(self.btn_search, 0)
        row_search.addWidget(self.btn_refresh, 0)

        root.addLayout(row_search)

        # Results table (left) and selected-product card (right) in a split layout
        mid_row = QHBoxLayout()
        mid_row.setSpacing(14)

        # Results table - left
        # Columns: Name | Short Code | Barcode | Company | Price (base/sell vertical) | Stock
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            t("name", self.lang) if t("name", self.lang) != "name" else "Name",
            t("short_code", self.lang) if t("short_code", self.lang) != "short_code" else "Short Code",
            t("barcode", self.lang) if t("barcode", self.lang) != "barcode" else "Barcode",
            t("company", self.lang) if t("company", self.lang) != "company" else "Company",
            t("price", self.lang) if t("price", self.lang) != "price" else "Price",
            t("stock", self.lang) if t("stock", self.lang) != "stock" else "Stock",
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(self.table.SelectionMode.SingleSelection)
        self.table.setEditTriggers(self.table.EditTrigger.NoEditTriggers)
        self.table.setObjectName("resultsTable")

        mid_row.addWidget(self.table, 3)

        # Selected product card - right
        card = QFrame()
        card.setObjectName("selectedCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(10, 12, 10, 12)
        card_layout.setSpacing(10)

        # Selected product title (big)
        self.lbl_selected = QLabel("")
        sel_font = QFont()
        sel_font.setPointSize(15)   # increased for readability
        sel_font.setBold(True)
        self.lbl_selected.setFont(sel_font)
        self.lbl_selected.setWordWrap(True)
        self.lbl_selected.setObjectName("selectedTitle")
        card_layout.addWidget(self.lbl_selected)

        # compact grid for small attributes (unit, supply pack, current stock)
        grid = QGridLayout()
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(6)

        # labels (smaller, muted) and values (bolder) - make them instance attrs so apply_language can update
        self.lbl_unit_label = QLabel(t("unit", self.lang) if t("unit", self.lang) != "unit" else "Unit")
        self.lbl_unit_label.setObjectName("metaLabel")
        self.lbl_unit = QLabel("")
        self.lbl_unit.setObjectName("metaValue")

        self.lbl_supply_label = QLabel(t("supply_pack_qty", self.lang) if t("supply_pack_qty", self.lang) != "supply_pack_qty" else "Supply / pack")
        self.lbl_supply_label.setObjectName("metaLabel")
        self.lbl_supply_pack = QLabel("")
        self.lbl_supply_pack.setObjectName("metaValue")

        self.lbl_current_label = QLabel(t("current_stock", self.lang) if t("current_stock", self.lang) != "current_stock" else "Current stock")
        self.lbl_current_label.setObjectName("metaLabel")
        self.lbl_current_stock = QLabel("")
        self.lbl_current_stock.setObjectName("metaValue")

        grid.addWidget(self.lbl_unit_label, 0, 0, Qt.AlignmentFlag.AlignLeft)
        grid.addWidget(self.lbl_unit, 1, 0, Qt.AlignmentFlag.AlignLeft)
        grid.addWidget(self.lbl_supply_label, 0, 1, Qt.AlignmentFlag.AlignLeft)
        grid.addWidget(self.lbl_supply_pack, 1, 1, Qt.AlignmentFlag.AlignLeft)
        grid.addWidget(self.lbl_current_label, 0, 2, Qt.AlignmentFlag.AlignLeft)
        grid.addWidget(self.lbl_current_stock, 1, 2, Qt.AlignmentFlag.AlignLeft)

        card_layout.addLayout(grid)

        # Projection area (prominent)
        proj_box = QFrame()
        proj_box.setObjectName("projBox")
        proj_layout = QHBoxLayout(proj_box)
        proj_layout.setContentsMargins(8, 8, 8, 8)
        proj_layout.setSpacing(12)

        # store labels to update their translations later
        self.lbl_added_label = QLabel(t("added_qty", self.lang) if t("added_qty", self.lang) != "added_qty" else "Added qty:")
        self.lbl_added_label.setObjectName("projLabel")
        self.lbl_added_qty = QLabel("0")
        big_font = QFont()
        big_font.setPointSize(16)
        big_font.setBold(True)
        self.lbl_added_qty.setFont(big_font)

        self.lbl_new_label = QLabel(t("new_stock", self.lang) if t("new_stock", self.lang) != "new_stock" else "New stock:")
        self.lbl_new_label.setObjectName("projLabel")
        self.lbl_new_stock = QLabel("0")
        self.lbl_new_stock.setFont(big_font)

        left_proj = QVBoxLayout()
        left_proj.addWidget(self.lbl_added_label)
        left_proj.addWidget(self.lbl_added_qty)

        right_proj = QVBoxLayout()
        right_proj.addWidget(self.lbl_new_label)
        right_proj.addWidget(self.lbl_new_stock)

        proj_layout.addLayout(left_proj)
        proj_layout.addLayout(right_proj)
        proj_layout.addStretch(1)

        card_layout.addWidget(proj_box)

        # Input controls (num packs, cost, reference) placed below card
        form_row = QHBoxLayout()
        form_row.setSpacing(8)

        # number of packs (store label for translation)
        self.lbl_num_packs_label = QLabel(t("num_packs", self.lang) if t("num_packs", self.lang) != "num_packs" else "Packs:")
        self.spin_num_packs = QSpinBox()
        self.spin_num_packs.setMinimum(1)
        self.spin_num_packs.setMaximum(1000000)
        self.spin_num_packs.setValue(1)
        self.spin_num_packs.setFixedHeight(34)
        self.spin_num_packs.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.spin_num_packs.setObjectName("numPacks")

        # cost input (store label)
        self.lbl_cost_label = QLabel(t("cost_total", self.lang) if t("cost_total", self.lang) != "cost_total" else "Cost:")
        self.spin_cost_total = QDoubleSpinBox()
        self.spin_cost_total.setMinimum(0.0)
        self.spin_cost_total.setMaximum(999999999.0)
        self.spin_cost_total.setDecimals(2)
        self.spin_cost_total.setFixedHeight(34)
        self.spin_cost_total.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.spin_cost_total.setPrefix("Rs ")
        self.spin_cost_total.setObjectName("costInput")

        # reference
        self.txt_reference = QLineEdit()
        self.txt_reference.setPlaceholderText(t("reference_id", self.lang) if t("reference_id", self.lang) != "reference_id" else "Reference ID (optional)")
        self.txt_reference.setFixedHeight(34)
        self.txt_reference.setObjectName("refInput")

        form_row.addWidget(self.lbl_num_packs_label)
        form_row.addWidget(self.spin_num_packs, 0)
        form_row.addWidget(self.lbl_cost_label)
        form_row.addWidget(self.spin_cost_total, 1)
        form_row.addWidget(self.txt_reference, 2)

        # combine card + form column
        right_col = QVBoxLayout()
        right_col.addWidget(card)
        right_col.addLayout(form_row)

        mid_row.addLayout(right_col, 2)

        root.addLayout(mid_row)

        # action buttons (receive / cancel)
        action_row = QHBoxLayout()
        action_row.setSpacing(8)
        self.btn_receive = QPushButton(t("receive", self.lang) if t("receive", self.lang) != "receive" else "Receive")
        self.btn_receive.setFixedHeight(36)
        self.btn_receive.setObjectName("primaryBtn")

        self.btn_cancel = QPushButton(t("cancel", self.lang) if t("cancel", self.lang) != "cancel" else "Cancel")
        self.btn_cancel.setFixedHeight(36)
        self.btn_cancel.setObjectName("secondaryBtn")

        action_row.addStretch(1)
        action_row.addWidget(self.btn_receive)
        action_row.addWidget(self.btn_cancel)

        root.addLayout(action_row)

        # small status
        self.lbl_status = QLabel("")
        f2 = QFont()
        f2.setPointSize(11)
        self.lbl_status.setFont(f2)
        root.addWidget(self.lbl_status)

    def _apply_styles(self):
        # modern clean stylesheet; bumped base font-size for readability
        self.search_input.setFixedHeight(50)
        self.setStyleSheet(
            """
            QWidget {
                background: qlineargradient(x1:0 y1:0, x2:1 y2:1, stop:0 #f7fbff, stop:1 #ffffff);
                color: #222;
                font-size: 18px; 
            }
            QLineEdit#searchInput {
                border: 1px solid rgba(30,30,60,0.06);
                padding: 8px;
                border-radius: 8px;
                background: #fff;
                font-size: 20px; 
            }
            QPushButton#primaryBtn {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #3b82f6, stop:1 #2563eb);
                color: white;
                border-radius: 8px;
                padding: 6px 14px;
                font-weight: 700;
            }
            QPushButton#primaryBtn:hover { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #4f9cff, stop:1 #2b71ff); }
            QPushButton#secondaryBtn {
                background: #eef3fb;
                color: #274d7a;
                border-radius: 8px;
                padding: 6px 12px;
            }
            QTableWidget#resultsTable {
                background: white;
                border: 1px solid rgba(30,30,60,0.06);
                border-radius: 8px;
                font-size: 16px;
            }
            QHeaderView::section {
                background: #f3f6fb;
                padding: 6px;
                border: none;
                font-weight: 700;
                font-size: 16px;
            }
            QTableWidget#resultsTable::item {
                padding: 6px;
            }
            QTableWidget#resultsTable::item:selected {
                background: rgb(9, 49, 100);
            }
            QFrame#selectedCard {
                border-radius: 8px;
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #ffffff, stop:1 #fbfdff);
                border: 1px solid rgba(30,30,60,0.06);
            }
            QLabel#selectedTitle {
                color: #12233b;
                font-size: 18px;
            }
            QLabel#metaLabel {
                color: #111827;
                font-size: 18px;
            }
            QLabel#metaValue {
                color: #111827;
                font-weight: 700;
                font-size: 18px;
            }
            QFrame#projBox {
                border-radius: 6px;
                background: linear-gradient(180deg, #f8fafc, #ffffff);
                border: 1px solid rgba(30,30,60,0.04);
            }
            QLabel.projLabel {
                color: #4b5563;
                font-size: 16px;
            }
            """
        )

    def _connect_signals(self):
        self.btn_search.clicked.connect(self.on_search)
        self.search_input.returnPressed.connect(self.on_search)
        self.btn_refresh.clicked.connect(self._on_refresh)
        self.table.cellDoubleClicked.connect(self._on_select_from_table)
        self.spin_num_packs.valueChanged.connect(self._recalculate_projection)
        self.btn_receive.clicked.connect(self._on_receive)
        self.btn_cancel.clicked.connect(self._clear_selection)

    # ---------------- Helpers ----------------
    def _format_decimal(self, v) -> str:
        try:
            d = Decimal(str(v))
            if d == d.to_integral():
                return str(int(d))
            return format(d.normalize(), 'f')
        except Exception:
            return str(v or "")

    def _format_price_pair(self, base_val, sell_val) -> str:
        """Return formatted multiline price string: Base on first line, Sell on second."""
        def fmt(v):
            try:
                dv = Decimal(str(v))
                # show no trailing zeros if integer-like, else 2 decimals for prices
                return f"{dv:.2f}"
            except Exception:
                return str(v or "")
        return f"{fmt(base_val)}\n{fmt(sell_val)}"

    def _name_with_pack(self, p: Dict[str, Any]) -> str:
        # similar to product_list_screen logic: choose name based on language then show packing if present
        en = p.get("en_name") or ""
        ur = p.get("ur_name") or ""
        name = en if (self.lang == "en" and en) else (ur if ur else en)
        pack = p.get("packing_size")
        unit = p.get("unit") or ""
        if pack is not None and str(pack).strip() != "":
            try:
                pd = Decimal(str(pack))
                if pd == pd.to_integral():
                    pack_str = str(int(pd))
                else:
                    pack_str = format(pd.normalize(), 'f')
            except Exception:
                pack_str = str(pack)
            return f"{name} ({pack_str} {unit})" if unit else f"{name} ({pack_str})"
        return name

    # ---------------- Actions ----------------
    def on_search(self):
        term = self.search_input.text().strip()
        if not term:
            QMessageBox.information(
                self,
                t("validation_title", self.lang) if t("validation_title", self.lang) != "validation_title" else "Validation",
                t("enter_search_term", self.lang) if t("enter_search_term", self.lang) != "enter_search_term" else "Enter a search term."
            )
            return
        try:
            results = product_service.search_products(term, limit=200)
        except Exception as exc:
            QMessageBox.critical(self, t("error", self.lang) if t("error", self.lang) != "error" else "Error", str(exc))
            return

        self._raw_results = [r for r in results if r is not None]
        self._populate_results_table()

    def _on_refresh(self):
        # clear search and reload default product listing (first 200)
        self.search_input.clear()
        self._raw_results = product_service.list_products(limit=200)
        self._populate_results_table()
        self._clear_selection()

    def _populate_results_table(self):
        rows = self._raw_results or []
        self.table.setRowCount(0)
        self.table.setRowCount(len(rows))
        for r, p in enumerate(rows):
            name_item = QTableWidgetItem(self._name_with_pack(p))
            name_item.setData(Qt.ItemDataRole.UserRole, p.get("id"))
            self.table.setItem(r, 0, name_item)
            self.table.setItem(r, 1, QTableWidgetItem(str(p.get("short_code") or "")))
            self.table.setItem(r, 2, QTableWidgetItem(str(p.get("barcode") or "")))
            self.table.setItem(r, 3, QTableWidgetItem(str(p.get("company") or "")))

            # Price column: base on top, sell below
            price_text = self._format_price_pair(p.get("base_price"), p.get("sell_price"))
            price_item = QTableWidgetItem(price_text)
            # allow multi-line display
            price_item.setData(Qt.ItemDataRole.DisplayRole, price_text)
            self.table.setItem(r, 4, price_item)

            self.table.setItem(r, 5, QTableWidgetItem(self._format_decimal(p.get("stock_qty"))))
        self.table.resizeRowsToContents()
        self.lbl_status.setText(f"{len(rows)} results")

    def _on_select_from_table(self, row: int, col: int):
        item = self.table.item(row, 0)
        if not item:
            return
        pid = item.data(Qt.ItemDataRole.UserRole)
        if not pid:
            return
        try:
            self.select_product(int(pid))
        except Exception as exc:
            QMessageBox.critical(self, t("error", self.lang) if t("error", self.lang) != "error" else "Error", str(exc))

    def select_product(self, product_id: int):
        p = product_service.get_product(product_id)
        if not p:
            QMessageBox.warning(self, t("error", self.lang) if t("error", self.lang) != "error" else "Error", "Product not found.")
            return
        self._selected_product = p
        # update details
        self.lbl_selected.setText(self._name_with_pack(p))
        self.lbl_unit.setText(str(p.get("unit") or ""))
        self.lbl_supply_pack.setText(self._format_decimal(p.get("supply_pack_qty") or 1))
        self.lbl_current_stock.setText(self._format_decimal(p.get("stock_qty") or Decimal("0")))
        # reset inputs/projections
        self.spin_num_packs.setValue(1)
        self.spin_cost_total.setValue(0.0)
        self.txt_reference.clear()
        self._recalculate_projection()

    def _recalculate_projection(self):
        if not self._selected_product:
            self.lbl_added_qty.setText("0")
            self.lbl_new_stock.setText("0")
            return
        try:
            supply = Decimal(str(self._selected_product.get("supply_pack_qty") or "1"))
        except Exception:
            supply = Decimal("1")
        num = Decimal(self.spin_num_packs.value())
        added = supply * num
        try:
            current = Decimal(str(self._selected_product.get("stock_qty") or "0"))
        except Exception:
            current = Decimal("0")
        new_stock = current + added
        self.lbl_added_qty.setText(self._format_decimal(added))
        self.lbl_new_stock.setText(self._format_decimal(new_stock))

    def _clear_selection(self):
        self._selected_product = None
        self.lbl_selected.setText("")
        self.lbl_unit.setText("")
        self.lbl_supply_pack.setText("")
        self.lbl_current_stock.setText("")
        self.lbl_added_qty.setText("0")
        self.lbl_new_stock.setText("0")
        self.spin_num_packs.setValue(1)
        self.spin_cost_total.setValue(0.0)
        self.txt_reference.clear()
        # optionally clear selection in table
        try:
            self.table.clearSelection()
        except Exception:
            pass

    def _on_receive(self):
        if not self._selected_product:
            QMessageBox.warning(
                self,
                t("validation_title", self.lang) if t("validation_title", self.lang) != "validation_title" else "Validation",
                t("select_product_first", self.lang) if t("select_product_first", self.lang) != "select_product_first" else "Please select a product first."
            )
            return
        num_packs = int(self.spin_num_packs.value())
        cost_total = Decimal(str(self.spin_cost_total.value())) if self.spin_cost_total.value() else None
        reference = self.txt_reference.text().strip() or None

        # get created_by if available
        try:
            cur_user = get_current_user()
            created_by = cur_user.get("id") if cur_user else None
        except Exception:
            created_by = None

        try:
            # call service
            stock_service.receive_packs(
                product_id=int(self._selected_product.get("id")),
                num_packs=num_packs,
                cost_total=cost_total,
                created_by=created_by,
                reference_id=reference,
            )
        except Exception as exc:
            QMessageBox.critical(self, t("error", self.lang) if t("error", self.lang) != "error" else "Error", f"Failed to receive packs:\n{exc}")
            return

        QMessageBox.information(
            self,
            t("success", self.lang) if t("success", self.lang) != "success" else "Success",
            t("receive_success_msg", self.lang) if t("receive_success_msg", self.lang) != "receive_success_msg" else "Stock updated."
        )
        # emit signal for other screens to refresh
        self.stock_received.emit()
        # refresh product data and UI
        try:
            # reload selected product to reflect new stock
            pid = int(self._selected_product.get("id"))
            self.select_product(pid)
        except Exception:
            self._clear_selection()

    # ---------------- Language ----------------
    def apply_language(self, lang: str):
        self.lang = lang
        # update placeholders / labels
        self.search_input.setPlaceholderText(
            t("search_products_placeholder", lang) if t("search_products_placeholder", lang) != "search_products_placeholder"
            else "Search by name, barcode or short code"
        )
        self.btn_search.setText(t("search", lang) if t("search", lang) != "search" else "Search")
        self.btn_refresh.setText(t("refresh", lang) if t("refresh", lang) != "refresh" else "Refresh")
        self.btn_receive.setText(t("receive", lang) if t("receive", lang) != "receive" else "Receive")
        self.btn_cancel.setText(t("cancel", lang) if t("cancel", lang) != "cancel" else "Cancel")

        # update table headers (including new Price column)
        self.table.setHorizontalHeaderLabels([
            t("name", lang) if t("name", lang) != "name" else "Name",
            t("short_code", lang) if t("short_code", lang) != "short_code" else "Short Code",
            t("barcode", lang) if t("barcode", lang) != "barcode" else "Barcode",
            t("company", lang) if t("company", lang) != "company" else "Company",
            t("price", lang) if t("price", lang) != "price" else "Price",
            t("stock", lang) if t("stock", lang) != "stock" else "Stock",
        ])

        # update labels in the selected card
        try:
            if self.lbl_unit_label:
                self.lbl_unit_label.setText(t("unit", lang) if t("unit", lang) != "unit" else "Unit")
            if self.lbl_supply_label:
                self.lbl_supply_label.setText(t("supply_pack_qty", lang) if t("supply_pack_qty", lang) != "supply_pack_qty" else "Supply / pack")
            if self.lbl_current_label:
                self.lbl_current_label.setText(t("current_stock", lang) if t("current_stock", lang) != "current_stock" else "Current stock")
            if self.lbl_added_label:
                self.lbl_added_label.setText(t("added_qty", lang) if t("added_qty", lang) != "added_qty" else "Added qty:")
            if self.lbl_new_label:
                self.lbl_new_label.setText(t("new_stock", lang) if t("new_stock", lang) != "new_stock" else "New stock:")
            if self.lbl_num_packs_label:
                self.lbl_num_packs_label.setText(t("num_packs", lang) if t("num_packs", lang) != "num_packs" else "Packs:")
            if self.lbl_cost_label:
                self.lbl_cost_label.setText(t("cost_total", lang) if t("cost_total", lang) != "cost_total" else "Cost:")
            # reference placeholder
            self.txt_reference.setPlaceholderText(t("reference_id", lang) if t("reference_id", lang) != "reference_id" else "Reference ID (optional)")
        except Exception:
            pass

        # re-populate table to ensure displayed name language and price text are updated
        self._populate_results_table()

        # update selected product labels if selected
        if self._selected_product:
            self.lbl_selected.setText(self._name_with_pack(self._selected_product))
            self.lbl_unit.setText(str(self._selected_product.get("unit") or ""))
            self.lbl_supply_pack.setText(self._format_decimal(self._selected_product.get("supply_pack_qty") or 1))
            self.lbl_current_stock.setText(self._format_decimal(self._selected_product.get("stock_qty") or 0))
            # projection values are recalculated using existing numeric values
            self._recalculate_projection()
