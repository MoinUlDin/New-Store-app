from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QMessageBox, QToolButton,
    QDialog, QDialogButtonBox
)
from PyQt6.QtGui import QFont, QCursor
from PyQt6.QtCore import Qt, pyqtSignal

from services.settings_service import get_setting
from services.user_service import authenticate, mark_current_user_by_id, get_current_user


class PasswordLineEdit(QLineEdit):
    """
    QLineEdit with an embedded show/hide toggle button inside the field.
    Usage: replace plain QLineEdit password field with PasswordLineEdit().
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("input")
        # create a compact tool button inside the line edit
        self._toggle = QToolButton(self)
        self._toggle.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._toggle.setCheckable(True)
        self._toggle.setChecked(False)
        self._toggle.setText("Show")
        # Light inline styling so it matches current look; doesn't override your global styles.
        self._toggle.setStyleSheet(
            "QToolButton { border: none; padding: 0 6px; background: transparent; }"
            "QToolButton:checked { font-weight: 500; }"
        )
        # initial echo mode is Password
        self.setEchoMode(QLineEdit.EchoMode.Password)

        # make room for the button on the right: width of button + 6px padding
        btn_w = self._toggle.sizeHint().width() or 50
        self.setTextMargins(0, 0, btn_w + 6, 0)

        # connect toggle
        self._toggle.toggled.connect(self._on_toggled)

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        # Position toggle at the far right inside the line edit
        h = self.height()
        btn_w = self._toggle.sizeHint().width()
        btn_h = self._toggle.sizeHint().height()
        x = self.width() - btn_w - 4
        y = max(0, (h - btn_h) // 2)-2
        self._toggle.move(x, y)

    def _on_toggled(self, checked: bool):
        # toggle echo mode and button text
        if checked:
            self.setEchoMode(QLineEdit.EchoMode.Normal)
            self._toggle.setText("Hide")
        else:
            self.setEchoMode(QLineEdit.EchoMode.Password)
            self._toggle.setText("Show")


class LoginScreen(QWidget):
    """
    Modern login screen with username + password.
    Includes a 'Forgot Password?' link that opens a modal to enter email.
    Reset sending is a placeholder (shows an info box) so you can wire it later.

    Emits:
        login_successful(str username, str email)
    """
    login_successful = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_user = get_current_user()
        self.title = get_setting("shop_name") or "Kiryana POS"

        self._build_ui()
        self._connect_signals()
        self._apply_styles()
        
        
    def _build_ui(self):
        # Outer layout to center the card
        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.setSpacing(0)

        outer.addStretch(1)

        # Horizontal centering
        hcenter = QHBoxLayout()
        hcenter.addStretch(1)

        # Card (main login panel)
        self.card = QWidget()
        self.card.setObjectName("card")
        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(32, 28, 32, 28)
        self.card_layout.setSpacing(16)
        self.card.setFixedWidth(420)
        self.card.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        # Brand / logo area
        self.lbl_logo = QLabel(self.title)
        logo_font = QFont()
        logo_font.setPointSize(18)
        logo_font.setBold(True)
        self.lbl_logo.setFont(logo_font)
        self.lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_sub = QLabel("Sign in to your account")
        sub_font = QFont()
        sub_font.setPointSize(10)
        self.lbl_sub.setFont(sub_font)
        self.lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_sub.setObjectName("subtitle")

        self.card_layout.addWidget(self.lbl_logo)
        self.card_layout.addWidget(self.lbl_sub)

        # Username input (only username, not username+email)
        self.input_user = QLineEdit()
        self.input_user.setPlaceholderText("Username")
        self.input_user.setObjectName("input")
        self.input_user.setClearButtonEnabled(True)
        self.input_user.setFixedHeight(40)

        # Password input (using PasswordLineEdit which contains the toggle inside the field)
        pw_row = QHBoxLayout()
        pw_row.setSpacing(8)
        self.input_pass = PasswordLineEdit()
        self.input_pass.setPlaceholderText("Password")
        self.input_pass.setFixedHeight(40)
        pw_row.addWidget(self.input_pass)

        # Forgot row (aligned to right)
        row_extra = QHBoxLayout()
        row_extra.setSpacing(8)
        row_extra.addStretch(1)
        self.btn_forgot = QPushButton("?Forgot Password")
        self.btn_forgot.setFlat(True)
        self.btn_forgot.setObjectName("linkButton")
        self.btn_forgot.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        row_extra.addWidget(self.btn_forgot)

        # Login button
        self.btn_login = QPushButton("Sign in")
        self.btn_login.setFixedHeight(44)
        self.btn_login.setObjectName("primaryButton")

        # Footer small text
        self.lbl_footer = QLabel("Don't have an account? Contact administrator.")
        footer_font = QFont()
        footer_font.setPointSize(9)
        self.lbl_footer.setFont(footer_font)
        self.lbl_footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_footer.setObjectName("footer")

        # Assemble into card
        self.card_layout.addWidget(self.input_user)
        self.card_layout.addLayout(pw_row)
        self.card_layout.addLayout(row_extra)
        self.card_layout.addWidget(self.btn_login)
        self.card_layout.addWidget(self.lbl_footer)

        # Add card into center layout
        hcenter.addWidget(self.card)
        hcenter.addStretch(1)

        outer.addLayout(hcenter)
        outer.addStretch(1)

        # Make Enter/Return comfortable:
        # pressing return in user -> go to password; in password -> attempt login
        self.input_user.returnPressed.connect(lambda: self.input_pass.setFocus())
        self.input_pass.returnPressed.connect(self.attempt_login)

        if self.current_user:
            username = self.current_user['username'] or ''
            self.input_user.setText(username)
            
    def _connect_signals(self):
        self.btn_login.clicked.connect(self.attempt_login)
        self.btn_forgot.clicked.connect(self.show_forgot_password_dialog)

    def _apply_styles(self):
        # A compact stylesheet for a modern look — unchanged except small addition for toolbutton spacing
        self.setStyleSheet(
            """
            QWidget {
                background: qlineargradient(x1:0 y1:0, x2:1 y2:1,
                    stop:0 #f6f8fb, stop:1 #ffffff);
            }
            QWidget#card {
                background: white;
                border-radius: 12px;
                border: 1px solid rgba(20, 20, 40, 0.06);
            }
            QLabel#subtitle {
                color: #5b6b7a;
                margin-bottom: 6px;
                font-size: 16px;
            }
            QLineEdit#input {
                border: 1px solid rgba(20,20,40,0.08);
                border-radius: 8px;
                padding-left: 12px;
                padding-right: 12px;
                background: #fbfdff;
                font-size: 16px;
            }
            QPushButton#primaryButton {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #2563eb);
                color: white;
                border-radius: 8px;
                font-weight: 600;
                border: none;
            }
            QPushButton#primaryButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #4f9cff, stop:1 #2b71ff);
            }
            QPushButton#linkButton, QPushButton#linkButtonSmall {
                color: #2563eb;
                background: transparent;
                border: none;
                text-decoration: underline;
            }
            QPushButton#linkButtonSmall {
                font-size: 14px;
            }
            QLabel#footer {
                color: #9aa4b2;
                margin-top: 8px;
                font-size: 16px;
            }
            QToolButton {
                background: transparent;
                border: none;
            }
            """
        )

    def attempt_login(self):
        username = self.input_user.text().strip()
        password = self.input_pass.text()
        if not username:
            QMessageBox.warning(self, "Validation", "Please enter username.")
            self.input_user.setFocus()
            return
        if not password:
            QMessageBox.warning(self, "Validation", "Please enter password.")
            self.input_pass.setFocus()
            return

        try:
            user = authenticate(username, password)
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Authentication failed:\n{exc}")
            return

        if not user:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")
            # clear the password for safety
            self.input_pass.clear()
            self.input_pass.setFocus()
            return

        # At this point authentication succeeded and authenticate() already updated last_login_at.
        user_id = user.get("id")
        user_email = user.get("email") or ""

        # Mark current user in DB (try helper first, otherwise fallback)
        try:
            mark_current_user_by_id(user_id)
        except Exception as exc:
            QMessageBox.warning(self, "Warning", f"Could not mark current user in DB:\n{exc}")

        # Emit signal for MainWindow to react
        self.login_successful.emit(user.get("username") or username, user_email)
        # clear password field
        self.input_pass.clear()

    # ------------------ Forgot password modal ------------------
    def show_forgot_password_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Reset password")
        dlg.setModal(True)
        dlg.setFixedWidth(420)
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        lbl = QLabel("Enter the email address associated with your account.\n"
                     "We will send a security code to this address.")
        lbl.setWordWrap(True)

        email_input = QLineEdit()
        email_input.setPlaceholderText("Email address")
        email_input.setFixedHeight(36)

        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)
        btn_box.button(QDialogButtonBox.StandardButton.Ok).setText("Send")
        btn_box.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancel")

        layout.addWidget(lbl)
        layout.addWidget(email_input)
        layout.addWidget(btn_box)

        def send_and_close():
            email = email_input.text().strip()
            if not email:
                QMessageBox.warning(dlg, "Validation", "Please enter an email address.")
                email_input.setFocus()
                return
            if "@" not in email or "." not in email:
                QMessageBox.warning(dlg, "Validation", "Please enter a valid email address.")
                email_input.setFocus()
                return
            # Placeholder for sending reset email; wire to your backend later
            QMessageBox.information(dlg, "Password reset",
                                    f"A reset security code would be sent to:\n{email}\n\n(Feature not implemented yet.)")
            dlg.accept()

        btn_box.accepted.connect(send_and_close)
        btn_box.rejected.connect(dlg.reject)

        dlg.exec()
