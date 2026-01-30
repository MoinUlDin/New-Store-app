from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QToolBar, QApplication, QToolButton,
    QSizePolicy, QStackedWidget
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap

from utils.i18n import t
from app.screens.order_screen import OrderScreen
from app.screens.settings import SettingScreen
from app.screens.add_update_item import AddUpdateItem
from app.screens.login_screen import LoginScreen
from app.screens.product_list_screen import ProductListScreen
from services.settings_service import get_all_settings
import os

# key:language, value:ur
# key:pass_on_startup, value: 0
# key:shop_name, value: 0
# key:shop_phone, value: 0
# key:shop_address, value: 0
# key: pass_on_product_update: value: 0
# key: pass_on_base_price_changed: value: 0
# key: pass_on_sell_price_changed: value: 0
# key: pass_on_stock_adjustment: value: 0
# key: pass_on_new_stock: value: 0

def icon_path(name: str) -> str:
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(root, "resources", "icons", name)

# A simple placeholder for screens not yet implemented
class PlaceholderScreen(QWidget):
    def __init__(self, name):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QWidget()) # Spacer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = get_all_settings()
        self.setGeometry(40, 50, 1000, 700) 
        self.toolbar_space = 25
        self.windo_title = self.settings.get("shop_name", "Stock Manager")
        # keep track of currently logged-in user
        self.current_user = None  # will be set to {"username":..., "email":...} after login

        # 1. Initialize the Stacked Widget
        self.stack = QStackedWidget()

        # 2. Initialize Screens
        self.order_screen = OrderScreen()
        self.settings_screen = SettingScreen()
        self.add_update_screen = AddUpdateItem()
        self.dashboard_screen = PlaceholderScreen("Dashboard")
        self.stock_list_screen = ProductListScreen()
        self.add_stock_screen = PlaceholderScreen("Add Stock")
        self.manage_stock_screen = PlaceholderScreen("Manage Stock")

        # Login screen (added)
        self.login_screen = LoginScreen()

        # 3. Add Screens to Stack (keep same ordering for existing indexes)
        self.stack.addWidget(self.dashboard_screen)      # Index 0
        self.stack.addWidget(self.order_screen)          # Index 1
        self.stack.addWidget(self.stock_list_screen)     # Index 2
        self.stack.addWidget(self.add_update_screen)     # Index 3
        self.stack.addWidget(self.add_stock_screen)      # Index 4
        self.stack.addWidget(self.manage_stock_screen)   # Index 5
        self.stack.addWidget(self.settings_screen)       # Index 6
        self.stack.addWidget(self.login_screen)          # Index 7 (login)

        # Build UI
        self._build_base_ui()
        
        # Connect to LanguageManager
        app = QApplication.instance()
        lm = getattr(app, "language_manager", None)
        
        if lm is not None:
            lm.language_changed.connect(self.apply_language)
            self.apply_language(lm.current)
        else:
            self.apply_language("ur")


        self.connect_signals()
        # Decide whether to show login screen on startup
        try:
            val = str(self.settings.get("pass_on_startup", "0")).strip()
            if val in ("1", "True", "true"):
                # show login, hide toolbar
                self.toolbar.hide()
                self.stack.setCurrentWidget(self.login_screen)
            else:
                # normal flow: show dashboard and toolbar
                self.toolbar.show()
                self.stack.setCurrentWidget(self.dashboard_screen)
        except Exception:
            # fallback - show dashboard
            self.toolbar.show()
            self.stack.setCurrentWidget(self.dashboard_screen)


    def _build_base_ui(self):
        self.build_toolbar()
        self.setCentralWidget(self.stack)

    def build_toolbar(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setMinimumHeight(85)
        self.addToolBar(toolbar)
        # store as instance attribute so we can show/hide later
        self.toolbar = toolbar

        def add_toolbutton(svg_name: str, text_key: str, screen=None) -> QToolButton:
            btn = QToolButton()
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            
            p = QPixmap(icon_path(svg_name))
            if not p.isNull():
                btn.setIcon(QIcon(p))
                btn.setIconSize(QSize(28, 28))
            
            btn.setText(t(text_key)) 
            btn.setAutoRaise(True)
            
            # Navigation logic: Switch stack index when clicked
            if screen:
                btn.clicked.connect(lambda _, s=screen: self.stack.setCurrentWidget(s))
            
            toolbar.addWidget(btn)
            return btn

        def add_gap(width: int = 12):
            spacer = QWidget()
            spacer.setFixedWidth(width)
            toolbar.addWidget(spacer)

        # Toolbar Buttons with navigation targets
        add_gap(int(self.toolbar_space*1.2))
        self.btn_home = add_toolbutton("trend.svg", "dashboard", self.dashboard_screen)
        
        add_gap(int(self.toolbar_space/2))
        toolbar.addSeparator()
        add_gap(int(self.toolbar_space/2))
        
        self.btn_pos = add_toolbutton("shoping_cart.svg", "new_order", self.order_screen)
        add_gap(self.toolbar_space)
        self.btn_stock_list = add_toolbutton("list.svg", "stock_list", self.stock_list_screen)
        add_gap(self.toolbar_space)
        self.btn_new_item = add_toolbutton("cross_circle.svg", "new_item", self.add_update_screen)
        add_gap(self.toolbar_space)
        self.btn_add_stock = add_toolbutton("package_check.svg", "add_stock", self.add_stock_screen)
        add_gap(self.toolbar_space)
        self.btn_manage_stock = add_toolbutton("arrow_out_up.svg", "manage_stock", self.manage_stock_screen)
        add_gap(self.toolbar_space)
        self.btn_settings = add_toolbutton("settings.svg", "settings", self.settings_screen)

    def connect_signals(self):
        self.login_screen.login_successful.connect(self._on_login_success)
        self.add_update_screen.item_added_updated.connect(self.stock_list_screen.load_products)

    def _on_login_success(self, username: str, email: str):
        """
        Called when LoginScreen emits login_successful.
        Stores current user, shows toolbar, and navigates to dashboard.
        """
        self.current_user = {"username": username, "email": email}
        # show toolbar and navigate
        self.toolbar.show()
        # ensure dashboard is visible
        self.stack.setCurrentWidget(self.dashboard_screen)
        # optional: update window title with username
        self.window_title = f'{self.windo_title}-{username}'
        self.setWindowTitle(self.window_title)

    def apply_language(self, lang: str):
        
        # Update Toolbar Labels
        self.btn_home.setText(t("dashboard", lang))
        self.btn_pos.setText(t("new_order", lang))
        self.btn_stock_list.setText(t("stock_list", lang))
        self.btn_new_item.setText(t("new_item", lang))
        self.btn_add_stock.setText(t("add_stock", lang))
        self.btn_manage_stock.setText(t("manage_stock", lang))
        self.btn_settings.setText(t("settings", lang))

        # Handle RTL/LTR
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if lang == "ur" else Qt.LayoutDirection.LeftToRight)
            
        # Update all screens in the stack
        for i in range(self.stack.count()):
            current_screen = self.stack.widget(i)
            if current_screen and hasattr(current_screen, "apply_language"):
                current_screen.apply_language(lang)
