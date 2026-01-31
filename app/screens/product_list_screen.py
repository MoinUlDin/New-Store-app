# app/screens/product_list_screen.py
from typing import List, Dict, Any, Optional
from decimal import Decimal

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel,
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QSizePolicy, QAbstractItemView, QWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from services import product_service
from data.db import get_connection
from services.settings_service import get_setting
from utils.product_list_screen_tr import t
from app.modals.confirm_password_dialog import ConfirmPasswordDialog


class ProductListScreen(QWidget):
    """
    Product list with search and filters.

    Signals:
      edit_requested(int) - emitted when user clicks Edit for a product (product_id)
      product_selected(int) - emitted when user double-clicks a product row
    """
    edit_requested = pyqtSignal(int)
    product_selected = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang = "ur"
        # try to pick app language from language_manager if available
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

        # internal state
        self._raw_products: List[Dict[str, Any]] = []
        # when a search is active this holds the search-filtered base list (before company/category filters)
        self._raw_products_filtered_by_search: Optional[List[Dict[str, Any]]] = None
        self._categories_map: Dict[int, str] = {}

        self._build_ui()
        self.load_filters()
        self.load_products()
        self._connect_buttons()

    # ---------------- UI ----------------
    def _connect_buttons(self):
        self.search_input.returnPressed.connect(self.on_search)
        self.btn_search.clicked.connect(self.on_search)
        self.cmb_company.currentIndexChanged.connect(self.on_filter_changed)
        self.cmb_category.currentIndexChanged.connect(self.on_filter_changed)
        self.btn_refresh.clicked.connect(self.load_products)
        self.btn_show_all.clicked.connect(self._on_show_all)
        self.table.cellDoubleClicked.connect(self._on_row_double_click)
        
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        # Top controls: search + company filter + category filter + refresh + show all
        ctrl_row = QHBoxLayout()
        ctrl_row.setSpacing(8)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(t("search_products_placeholder", self.lang) if t("search_products_placeholder", self.lang) != "search_products_placeholder" else "Search by name, barcode or short code")
        self.search_input.setFixedHeight(34)

        self.btn_search = QPushButton(t("search", self.lang) if t("search", self.lang) != "search" else "Search")
        self.btn_search.setFixedHeight(34)
        
        self.cmb_company = QComboBox()
        self.cmb_company.setFixedHeight(34)
        
        self.cmb_category = QComboBox()
        self.cmb_category.setFixedHeight(34)
        self.cmb_category.currentIndexChanged.connect(self.on_filter_changed)

        self.btn_refresh = QPushButton(t("refresh", self.lang) if t("refresh", self.lang) != "refresh" else "Refresh")
        self.btn_refresh.setFixedHeight(34)

        # Show All button (clears search + filters)
        
        self.btn_show_all = QPushButton(t("show_all", self.lang))
        self.btn_show_all.setFixedHeight(34)

        ctrl_row.addWidget(self.search_input, 3)
        ctrl_row.addWidget(self.btn_search, 0)
        ctrl_row.addWidget(self.cmb_company, 1)
        ctrl_row.addWidget(self.cmb_category, 1)
        ctrl_row.addWidget(self.btn_refresh, 0)
        ctrl_row.addWidget(self.btn_show_all, 0)

        root.addLayout(ctrl_row)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)  # name, short_code, category, company, base_price, sell_price, stock/reorder, actions
        self.table.setHorizontalHeaderLabels([
            t("name", self.lang) if t("name", self.lang) != "name" else "Name",
            t("short_code", self.lang) if t("short_code", self.lang) != "short_code" else "Short Code",
            t("category", self.lang) if t("category", self.lang) != "category" else "Category",
            t("company", self.lang) if t("company", self.lang) != "company" else "Company",
            t("base_price", self.lang) if t("base_price", self.lang) != "base_price" else "Base",
            t("sell_price", self.lang) if t("sell_price", self.lang) != "sell_price" else "Sell",
            t("stock", self.lang) if t("stock", self.lang) != "stock" else "Stock / Reorder",
            t("actions", self.lang) if t("actions", self.lang) != "actions" else "Actions",
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # name stretches
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)

        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        
        root.addWidget(self.table, 1)

        # small status/footer
        self.lbl_status = QLabel("")
        f = QFont()
        f.setPointSize(9)
        self.lbl_status.setFont(f)
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignLeft)
        root.addWidget(self.lbl_status)

    # ---------------- Data helpers ----------------
    def _fetch_companies(self) -> List[str]:
        conn = get_connection()
        cur = conn.execute("SELECT DISTINCT company FROM products WHERE company IS NOT NULL AND company <> '' ORDER BY company")
        rows = cur.fetchall()
        return [r["company"] for r in rows]

    def _fetch_categories(self) -> Dict[int, str]:
        conn = get_connection()
        cur = conn.execute("SELECT id, name FROM categories ORDER BY name")
        rows = cur.fetchall()
        return {r["id"]: r["name"] for r in rows}

    def load_filters(self, lang: Optional[str] = None):
        """
        Populate company and category combos.
        Clears and rebuilds the entire combo, including the translated first item.
        Attempts to preserve previous selection where possible.
        """
        if lang is None:
            lang = getattr(self, "lang", "ur")

        # remember previous selections (by data) so we can restore if possible
        try:
            prev_company = self.cmb_company.currentData() if self.cmb_company.count() > 0 else None
        except Exception:
            prev_company = None
        try:
            prev_category = self.cmb_category.currentData() if self.cmb_category.count() > 0 else None
        except Exception:
            prev_category = None

        # fetch fresh lists
        companies = self._fetch_companies()
        categories = self._fetch_categories()
        # cache categories map
        self._categories_map = categories

        # build translated "All ..." labels (fall back to sensible defaults)
        all_companies_label = t("all_companies", lang) if t("all_companies", lang) != "all_companies" else ("All companies" if lang == "en" else "All companies")
        all_categories_label = t("all_categories", lang) if t("all_categories", lang) != "all_categories" else ("All categories" if lang == "en" else "All categories")

        # Rebuild company combo
        self.cmb_company.blockSignals(True)
        try:
            self.cmb_company.clear()
            self.cmb_company.addItem(all_companies_label, userData="__all__")
            for c in companies:
                self.cmb_company.addItem(c, userData=c)

            # try to restore previous company selection
            if prev_company is not None:
                restored = False
                for i in range(self.cmb_company.count()):
                    try:
                        if str(self.cmb_company.itemData(i)) == str(prev_company):
                            self.cmb_company.setCurrentIndex(i)
                            restored = True
                            break
                    except Exception:
                        continue
                if not restored:
                    self.cmb_company.setCurrentIndex(0)
            else:
                self.cmb_company.setCurrentIndex(0)
        finally:
            self.cmb_company.blockSignals(False)

        # Rebuild category combo
        self.cmb_category.blockSignals(True)
        try:
            self.cmb_category.clear()
            self.cmb_category.addItem(all_categories_label, userData="__all__")
            for cid, name in categories.items():
                self.cmb_category.addItem(name, userData=cid)

            # try to restore previous category selection
            if prev_category is not None:
                restored = False
                for i in range(self.cmb_category.count()):
                    try:
                        if str(self.cmb_category.itemData(i)) == str(prev_category):
                            self.cmb_category.setCurrentIndex(i)
                            restored = True
                            break
                    except Exception:
                        continue
                if not restored:
                    self.cmb_category.setCurrentIndex(0)
            else:
                self.cmb_category.setCurrentIndex(0)
        finally:
            self.cmb_category.blockSignals(False)


    def load_products(self):
        """
        Load initial product list (no search) and apply client-side filters.
        Resets any active search state.
        """
        self._raw_products = product_service.list_products()
        # clear any active search state
        self._raw_products_filtered_by_search = None
        # make sure filters are fresh
        try:
            self.load_filters()
        except Exception:
            pass
        self._apply_filters_and_render()
        self._update_status()

    def _matches_search(self, p: Dict[str, Any], term: str) -> bool:
        """
        Case-insensitive substring match for en_name, ur_name, short_code, barcode.
        """
        if not term:
            return True
        lowered = term.lower()
        en = (p.get("en_name") or "")
        ur = (p.get("ur_name") or "")
        sc = (p.get("short_code") or "")
        bc = (p.get("barcode") or "")

        try:
            en_s = str(en).lower()
        except Exception:
            en_s = ""
        try:
            ur_s = str(ur).lower()
        except Exception:
            ur_s = ""
        try:
            sc_s = str(sc).lower()
        except Exception:
            sc_s = ""
        try:
            bc_s = str(bc).lower()
        except Exception:
            bc_s = ""

        return (lowered in en_s) or (lowered in ur_s) or (lowered in sc_s) or (lowered in bc_s)

    def on_search(self):
        term = self.search_input.text().strip()
        if not term:
            # empty -> clear search state and reload normal list (but keep filters)
            self._raw_products_filtered_by_search = None
            self._apply_filters_and_render()
            self._update_status()
            return

        # Client-side case-insensitive substring search across name (ur/en), barcode, short_code
        base = [p for p in (self._raw_products or []) if p is not None and self._matches_search(p, term)]
        self._raw_products_filtered_by_search = base
        # render filtered results but still allow category/company filters
        self._apply_filters_and_render_from_search(base)
        self._update_status(search_term=term)

    def on_filter_changed(self):
        # called when company/category filter changes
        term = self.search_input.text().strip()
        if term:
            # if search text present, start from search-filtered base (compute if needed)
            if self._raw_products_filtered_by_search is None:
                # compute filtered_by_search from raw products
                self._raw_products_filtered_by_search = [p for p in (self._raw_products or []) if p is not None and self._matches_search(p, term)]
            base = self._raw_products_filtered_by_search
        else:
            base = self._raw_products or []
        self._apply_filters_and_render_from_search(base)
        self._update_status(search_term=term if term else None)

    def _apply_filters_and_render(self):
        # read selected filters
        selected_company = self.cmb_company.currentData()
        selected_category = self.cmb_category.currentData()

        filtered = []
        for p in self._raw_products:
            if p is None:
                continue
            if selected_company and selected_company != "__all__":
                comp = p.get("company") or ""
                if comp != selected_company:
                    continue
            if selected_category and selected_category != "__all__":
                cat_id = p.get("category_id")
                # compare string/int robustly
                if str(cat_id) != str(selected_category):
                    continue
            filtered.append(p)
        self._render_table(filtered)

    def _apply_filters_and_render_from_search(self, base_products: List[Dict[str, Any]]):
        """
        Apply company/category filters to the provided base_products (which may be
        the full raw list or a search-filtered subset) and then render.
        """
        selected_company = self.cmb_company.currentData()
        selected_category = self.cmb_category.currentData()

        filtered = []
        for p in base_products:
            if p is None:
                continue
            if selected_company and selected_company != "__all__":
                comp = p.get("company") or ""
                if comp != selected_company:
                    continue
            if selected_category and selected_category != "__all__":
                cat_id = p.get("category_id")
                if str(cat_id) != str(selected_category):
                    continue
            filtered.append(p)
        self._render_table(filtered)

    def _name_with_pack(self, product: Dict[str, Any]) -> str:
        # choose name based on language; fall back to ur_name when en missing
        en = product.get("en_name") or ""
        ur = product.get("ur_name") or ""
        if self.lang == "en" and en:
            name = en
        else:
            name = ur if ur else en

        # add packing (packing_size + unit) if present
        packing = product.get("packing_size")
        unit = t(product.get("unit") or "", self.lang)
        if packing is not None and str(packing).strip() != "":
            # display integer when possible, otherwise raw
            try:
                pack_dec = Decimal(str(packing))
                if pack_dec == pack_dec.to_integral():
                    pack_str = f"{int(pack_dec)}"
                else:
                    pack_str = f"{pack_dec.normalize()}"
            except Exception:
                pack_str = str(packing)
            return f"{name} - ({pack_str} {unit})" if unit else f"{name} - ({pack_str})"
        return name

    def _stock_cell_text(self, product: Dict[str, Any]) -> str:
        # stock_qty on first line, reorder_threshold on second line
        stock = product.get("stock_qty") or Decimal("0")
        reorder = product.get("reorder_threshold") or Decimal("0")
        # format numbers: if integer-like show integer, else show up to 3 decimals
        def fmt(v: Decimal) -> str:
            try:
                if v == v.to_integral():
                    return str(int(v))
                else:
                    # trim trailing zeros
                    s = format(v.normalize(), 'f')
                    return s
            except Exception:
                return str(v)
        return f"{fmt(stock)}\n{t('reorder', self.lang) if t('reorder', self.lang) != 'reorder' else 'Reorder'}: {fmt(reorder)}"

    def _render_table(self, products: List[Dict[str, Any]]):
        self.table.setRowCount(0)
        rows = products
        self.table.setRowCount(len(rows))
        for r, p in enumerate(rows):
            # Name
            name_item = QTableWidgetItem(self._name_with_pack(p))
            name_item.setData(Qt.ItemDataRole.UserRole, p.get("id"))
            self.table.setItem(r, 0, name_item)

            # short_code
            sc = p.get("short_code") or ""
            self.table.setItem(r, 1, QTableWidgetItem(sc))

            # category name (lookup)
            cat_id = p.get("category_id")
            cat_name = self._categories_map.get(cat_id) if getattr(self, "_categories_map", None) else ""
            self.table.setItem(r, 2, QTableWidgetItem(cat_name or ""))

            # company
            self.table.setItem(r, 3, QTableWidgetItem(p.get("company") or ""))

            # base_price & sell_price - format with 2 decimals
            def fmt_price(v):
                try:
                    dv = Decimal(str(v))
                    return f"{dv:.2f}"
                except Exception:
                    return str(v or "")
            self.table.setItem(r, 4, QTableWidgetItem(fmt_price(p.get("base_price"))))
            self.table.setItem(r, 5, QTableWidgetItem(fmt_price(p.get("sell_price"))))

            # stock/reorder (multi-line)
            stock_item = QTableWidgetItem(self._stock_cell_text(p))
            stock_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(r, 6, stock_item)

            # actions - Edit / Delete buttons
            actions_widget = QWidget()
            ah = QHBoxLayout(actions_widget)
            ah.setContentsMargins(4, 2, 4, 2)
            ah.setSpacing(6)

            btn_edit = QPushButton(t("edit", self.lang) if t("edit", self.lang) != "edit" else "Edit")
            btn_edit.setProperty("product_id", p.get("id"))
            btn_edit.setFixedHeight(28)
            btn_edit.clicked.connect(self._on_edit_clicked)

            btn_del = QPushButton(t("delete", self.lang) if t("delete", self.lang) != "delete" else "Delete")
            btn_del.setProperty("product_id", p.get("id"))
            btn_del.setFixedHeight(28)
            btn_del.clicked.connect(self._on_delete_clicked)

            ah.addWidget(btn_edit)
            ah.addWidget(btn_del)
            ah.addStretch(1)

            self.table.setCellWidget(r, 7, actions_widget)

        # ensure header visuals
        self.table.resizeRowsToContents()
        self.table.verticalHeader().setVisible(False)

    # ---------------- Actions ----------------
    def _on_edit_clicked(self):
        btn = self.sender()
        if not btn:
            return
        pid = btn.property("product_id")
        try:
            pid = int(pid)
        except Exception:
            return
        # emit so parent (MainWindow) can pick and navigate to edit screen
        self.edit_requested.emit(pid)

    def _on_delete_clicked(self):
         
        btn = self.sender()
        if not btn:
            return
        pid = btn.property("product_id")
        try:
            pid = int(pid)
        except Exception:
            return
        confirm = QMessageBox.question(
            self,
            t("confirm_delete_title", self.lang) if t("confirm_delete_title", self.lang) != "confirm_delete_title" else "Confirm",
            t("confirm_delete_product", self.lang).format(id=pid) if t("confirm_delete_product", self.lang) != "confirm_delete_product" else f"Delete product (id={pid})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        
        dlg = ConfirmPasswordDialog(self, reason="Confirm delete", max_attempts=3)
        ok = dlg.exec_confirm()
        if not ok:
            return
        
        try:
            product_service.delete_product(pid)
            QMessageBox.information(self, t("deleted", self.lang) if t("deleted", self.lang) != "deleted" else "Deleted", t("product_deleted", self.lang) if t("product_deleted", self.lang) != "product_deleted" else "Product deleted.")
            self.load_filters()
            self.load_products()
        except Exception as exc:
            QMessageBox.critical(self, t("error", self.lang) if t("error", self.lang) != "error" else "Error", str(exc))

    def _on_row_double_click(self, row: int, col: int):
        item = self.table.item(row, 0)
        if not item:
            return
        pid = item.data(Qt.ItemDataRole.UserRole)
        if pid:
            try:
                pid = int(pid)
            except Exception:
                return
            self.product_selected.emit(pid)

    def _update_status(self, search_term: Optional[str] = None):
        # prefer the actual displayed row count
        count = self.table.rowCount()
        if search_term:
            self.lbl_status.setText(f"{count} results for '{search_term}'")
        else:
            self.lbl_status.setText(f"{count} products loaded")

    def _on_show_all(self):
        # clear search + filters and reload everything
        self.search_input.clear()
        # reset combos to first index
        try:
            self.cmb_company.setCurrentIndex(0)
        except Exception:
            pass
        try:
            self.cmb_category.setCurrentIndex(0)
        except Exception:
            pass
        self.load_products()

    # ---------------- Language ----------------
    def apply_language(self, lang: str):
        self.lang = lang
        # update UI labels & placeholders
        self.search_input.setPlaceholderText(
            t("search_products_placeholder", lang)
            if t("search_products_placeholder", lang) != "search_products_placeholder"
            else "Search by name, barcode or short code"
        )
        self.btn_search.setText(t("search", lang) if t("search", lang) != "search" else "Search")
        self.btn_refresh.setText(t("refresh", lang) if t("refresh", lang) != "refresh" else "Refresh")

        # update show all label (use translation if available)
        self.btn_show_all.setText(t("show_all", lang))
 

        # update table headers
        self.table.setHorizontalHeaderLabels([
            t("name", lang) if t("name", lang) != "name" else "Name",
            t("short_code", lang) if t("short_code", lang) != "short_code" else "Short Code",
            t("category", lang) if t("category", lang) != "category" else "Category",
            t("company", lang) if t("company", lang) != "company" else "Company",
            t("base_price", lang) if t("base_price", lang) != "base_price" else "Base",
            t("sell_price", lang) if t("sell_price", lang) != "sell_price" else "Sell",
            t("stock", lang) if t("stock", lang) != "stock" else "Stock / Reorder",
            t("actions", lang) if t("actions", lang) != "actions" else "Actions",
        ])

        # reload filters so the list of companies/categories is up-to-date
        try:
            self.load_filters()
        except Exception:
            # ignore failures here to keep UI responsive
            pass


        # re-render table to refresh name language (respecting current search/filter state)
        if hasattr(self, "_raw_products"):
            if self._raw_products_filtered_by_search is not None:
                # if search active, reapply filters on that base
                self._apply_filters_and_render_from_search(self._raw_products_filtered_by_search)
            else:
                self._apply_filters_and_render()
