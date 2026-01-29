from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QLineEdit, QPushButton, QCheckBox, QApplication
from PyQt6.QtCore import Qt
from utils.settings_screen_tr import t
from services import settings_service

class SettingScreen(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()
        
    
    def _init_ui(self):
        self._create_components()
        self._design()
        
    
    def _create_components(self):
        # Layout and Frames
        self.main_layout = QHBoxLayout()
        self.right_layout = QVBoxLayout()
        self.left_layout = QVBoxLayout()
        self.general_frame = QFrame()
        self.lang_frame = QFrame()
        self.secr_frame = QFrame()
        
        # Lables
        self.lbl_title = QLabel()
        self.lbl_general = QLabel()
        self.lbl_phone = QLabel()
        self.lbl_address = QLabel()
        self.lbl_lang = QLabel()
        self.lbl_secr = QLabel()
        self.lbl_shop_name = QLabel()
        self.lbl_old_pass = QLabel()
        self.lbl_new_pass = QLabel()

        # Inputs CheckBox
        self.txt_shop_name = QLineEdit()
        self.txt_phone = QLineEdit()
        self.txt_address = QLineEdit()
        self.txt_old_pass = QLineEdit()
        self.txt_new_pass = QLineEdit()
        self.txt_confirm_pass = QLineEdit()
        self.chk_lang = QCheckBox()
    
    def _design(self):
        self.right_layout.addWidget(self.general_frame)
        self.right_layout.addWidget(self.lang_frame)
        self.left_layout.addWidget(self.secr_frame)

        # General Frame
        self.general_frame.addWiget()
        
        
    def _apply_styles(self):
        pass
    
