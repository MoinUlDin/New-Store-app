# File: app/screens/settings_screen.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QLineEdit, QPushButton, QCheckBox, QApplication
from PyQt6.QtCore import Qt
from utils.settings_screen_tr import t
from services import settings_service

class SettingScreen(QWidget):
    def __init__(self):
        super().__init__()
        
        
        self._create_components()        
        
        self.cards_layout.addWidget(self.security_card)
        self.cards_layout.addWidget(self.lang_card)
        self.cards_layout.addWidget(self.general_card)

    def _create_components(self):
        self.main_layout = QVBoxLayout(self)
        
        # Header
        self.lbl_title = QLabel()
        self.lbl_title.setStyleSheet("font-size: 28px; font-weight: bold;")
        self.main_layout.addWidget(self.lbl_title)
        
        # Content Layout
        self.cards_layout = QHBoxLayout()
        self.main_layout.addLayout(self.cards_layout)
        
        # 1. Security Card
        self.security_card = self._create_card("security")
        self._build_security_ui()
        
        # 2. Language Card
        self.lang_card = self._create_card("language")
        self._build_language_ui()
        
        # 3. General Card
        self.general_card = self._create_card("general")
        self._build_general_ui()
        
        
    def _create_card(self, title_key):
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setStyleSheet("background-color: #fcfcfc; ")
        layout = QVBoxLayout(frame)
        title = QLabel(t(title_key))
        title.setProperty("lang_key", title_key)
        title.setStyleSheet("font-size: 20px; color: #2e7d32;")
        layout.addWidget(title)
        return frame

    def _build_general_ui(self):
        layout = self.general_card.layout()
        self.lbl_shop_name = QLabel()
        self.edit_shop_name = QLineEdit()
        
        # Load current name from DB
        current_name = settings_service.get_setting("shop_name") or "بسم اللہ کریانہ اسٹور"
        self.edit_shop_name.setText(current_name)
        
        self.btn_save_general = QPushButton()
        self.btn_save_general.setStyleSheet("background-color: #2e7d32; color: white;")
        self.btn_save_general.clicked.connect(self.save_general_settings)

        layout.addWidget(self.lbl_shop_name, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.edit_shop_name)
        layout.addWidget(self.btn_save_general)

    def _build_language_ui(self):
        layout = self.lang_card.layout()
        h_layout = QHBoxLayout()
        self.lbl_en = QLabel("English")
        self.lang_toggle = QCheckBox() # Acting as the toggle switch
        self.lbl_ur = QLabel("اردو")
        
        lm = getattr(QApplication.instance(), "language_manager", None)
        self.lang_toggle.setChecked(lm.current == "ur" if lm else True)
        self.lang_toggle.stateChanged.connect(self.toggle_language)

        # h_layout.addStretch()
        h_layout.addWidget(self.lbl_en)
        h_layout.addWidget(self.lang_toggle)
        h_layout.addWidget(self.lbl_ur)
        layout.addLayout(h_layout)

    def _build_security_ui(self):
        # Placeholder for password inputs (per image)
        layout = self.security_card.layout()
        self.edit_old_pass = QLineEdit()
        self.edit_old_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.edit_new_pass = QLineEdit()
        self.edit_new_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.edit_confirm_pass = QLineEdit()
        self.edit_confirm_pass.setEchoMode(QLineEdit.EchoMode.Password)
        
        layout.addWidget(self.edit_old_pass)
        layout.addWidget(self.edit_new_pass)
        layout.addWidget(self.edit_confirm_pass)

    def save_general_settings(self):
        name = self.edit_shop_name.text()
        settings_service.set_setting("shop_name", name) #
        print(f"Saved shop name: {name}")

    def toggle_language(self, state):
        lang = "ur" if state == 2 else "en"
        lm = getattr(QApplication.instance(), "language_manager", None)
        if lm:
            lm.set_language(lang)

    def apply_language(self, lang: str):
        self.lbl_title.setText(t("system_settings", lang))
        self.lbl_shop_name.setText(t("shop_name", lang))
        self.btn_save_general.setText(t("save", lang))
        
        # place holders text for input
        self.edit_confirm_pass.setPlaceholderText(t('confirm_pass', lang))
        self.edit_new_pass.setPlaceholderText(t('new_pass', lang))
        self.edit_old_pass.setPlaceholderText(t('old_pass', lang))
        
        # Update card titles
        for card in [self.security_card, self.lang_card, self.general_card]:
            title_lbl = card.layout().itemAt(0).widget()
            title_lbl.setText(t(title_lbl.property("lang_key"), lang))
        
        self.setLayoutDirection(Qt.LayoutDirection.LeftToRight if lang == "ur" else Qt.LayoutDirection.RightToLeft)