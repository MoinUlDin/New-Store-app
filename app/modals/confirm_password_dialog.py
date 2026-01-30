# app/screens/confirm_password_dialog.py

from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QDialogButtonBox, QMessageBox, QWidget, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor, QFont, QIcon
from PyQt6.QtWidgets import QGraphicsDropShadowEffect

from services.user_service import get_current_user, authenticate
from services.settings_service import get_setting
from PyQt6.QtWidgets import QApplication

# translator - create utils/confirm_password_tr.py with translations (see keys used below)
from utils.confirm_password_tr import t

class ConfirmPasswordDialog(QDialog):
    """
    Modernized Confirm Password dialog with language support.

    Usage:
        dlg = ConfirmPasswordDialog(parent, reason="Confirm delete", max_attempts=3)
        ok = dlg.exec_confirm()
        if ok:
            # proceed
        else:
            # cancelled / invalid password
    """

    def __init__(self, parent: Optional[QWidget] = None, reason: Optional[str] = None, max_attempts: int = 3):
        super().__init__(parent)

        # detect language: language_manager -> settings -> fallback 'ur'
        self.lang = "ur"
        try:
            app = QApplication.instance()
            lm = getattr(app, "language_manager", None)
            if lm is not None and hasattr(lm, "current"):
                self.lang = lm.current
            else:
                kling = get_setting("language")
                if kling:
                    self.lang = kling
        except Exception:
            self.lang = "ur"

        # dialog basics
        self.setWindowTitle(t("confirm_password_title", self.lang) if t("confirm_password_title", self.lang) != "confirm_password_title" else "Confirm password")
        self.setModal(True)
        self.setMinimumWidth(420)

        self._reason = reason or ""
        self._attempts_left = max(1, max_attempts)
        self._result = False

        self._build_ui()
        self._connect_signals()
        self._apply_styles()

    def _build_ui(self):
        # Outer layout
        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(10)

        # Card frame (so we can style and add shadow)
        self.card = QFrame()
        self.card.setObjectName("confirmCard")
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(18, 16, 18, 16)
        card_layout.setSpacing(10)

        # Title row (icon + title)
        title_row = QHBoxLayout()
        title_row.setSpacing(8)

        # optional small icon (use unicode lock as fallback)
        lbl_icon = QLabel("🔒")
        lbl_icon.setFixedWidth(36)
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(16)
        lbl_icon.setFont(font)

        title_text = QLabel(t("confirm_password_title", self.lang) if t("confirm_password_title", self.lang) != "confirm_password_title" else "Confirm password")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_text.setFont(title_font)

        title_row.addWidget(lbl_icon)
        title_row.addWidget(title_text)
        title_row.addStretch(1)

        card_layout.addLayout(title_row)

        # subtitle / reason
        subtitle = self._reason or (t("confirm_password_prompt", self.lang) if t("confirm_password_prompt", self.lang) != "confirm_password_prompt" else "Enter your password to continue")
        lbl_sub = QLabel(subtitle)
        lbl_sub.setWordWrap(True)
        lbl_sub.setObjectName("subtitle")
        card_layout.addWidget(lbl_sub)

        # password row: password field + show/hide link-like button
        pw_row = QHBoxLayout()
        pw_row.setSpacing(6)

        self.input_pass = QLineEdit()
        self.input_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_pass.setPlaceholderText(t("enter_password_ph", self.lang) if t("enter_password_ph", self.lang) != "enter_password_ph" else "Password")
        self.input_pass.setFixedHeight(36)
        self.input_pass.setObjectName("passwordInput")

        self.btn_toggle = QPushButton(t("show", self.lang) if t("show", self.lang) != "show" else "Show")
        self.btn_toggle.setCheckable(True)
        self.btn_toggle.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_toggle.setObjectName("toggleLink")
        self.btn_toggle.setFixedHeight(28)
        self.btn_toggle.setFixedWidth(72)

        pw_row.addWidget(self.input_pass, 1)
        pw_row.addWidget(self.btn_toggle)

        card_layout.addLayout(pw_row)

        # feedback label
        self.lbl_feedback = QLabel("")
        self.lbl_feedback.setObjectName("feedback")
        self.lbl_feedback.setWordWrap(False)
        card_layout.addWidget(self.lbl_feedback)

        # buttons
        self.btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        ok_text = t("confirm", self.lang) if t("confirm", self.lang) != "confirm" else "Confirm"
        cancel_text = t("cancel", self.lang) if t("cancel", self.lang) != "cancel" else "Cancel"
        self.btn_box.button(QDialogButtonBox.StandardButton.Ok).setText(ok_text)
        self.btn_box.button(QDialogButtonBox.StandardButton.Cancel).setText(cancel_text)

        card_layout.addWidget(self.btn_box)

        outer.addWidget(self.card)

        # Enter key submits
        self.input_pass.returnPressed.connect(self._on_confirm_clicked)

    def _connect_signals(self):
        self.btn_toggle.toggled.connect(self._toggle_show)
        self.btn_box.accepted.connect(self._on_confirm_clicked)
        self.btn_box.rejected.connect(self._on_cancel)

    def _apply_styles(self):
        # subtle shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 6)
        shadow.setColor(Qt.GlobalColor.black)
        self.card.setGraphicsEffect(shadow)

        # stylesheet
        self.setStyleSheet(
            f"""
            QWidget {{
                background: qlineargradient(x1:0 y1:0, x2:1 y2:1, stop:0 #f6f8fb, stop:1 #ffffff);
            }}
            QFrame#confirmCard {{
                background: #ffffff;
                border-radius: 10px;
                border: 1px solid rgba(20,20,40,0.06);
            }}
            QLabel#subtitle {{
                color: #5b6b7a;
                margin-bottom: 6px;
            }}
            QLineEdit#passwordInput {{
                border: 1px solid rgba(20,20,40,0.08);
                border-radius: 8px;
                padding-left: 10px;
                font-size: 13px;
                background: #fbfdff;
            }}
            QPushButton#toggleLink {{
                color: #2563eb;
                background: transparent;
                border: none;
                text-decoration: underline;
                font-weight: 600;
            }}
            QLabel#feedback {{
                color: #b91c1c;
                min-height: 18px;
            }}
            """
        )

    def _toggle_show(self, checked: bool):
        if checked:
            self.input_pass.setEchoMode(QLineEdit.EchoMode.Normal)
            self.btn_toggle.setText(t("hide", self.lang) if t("hide", self.lang) != "hide" else "Hide")
        else:
            self.input_pass.setEchoMode(QLineEdit.EchoMode.Password)
            self.btn_toggle.setText(t("show", self.lang) if t("show", self.lang) != "show" else "Show")

    def _on_cancel(self):
        self._result = False
        self.reject()

    def _on_confirm_clicked(self):
        """
        Verify the password for the currently marked user.
        """
        pw = self.input_pass.text() or ""
        if not pw:
            QMessageBox.warning(self, t("validation_title", self.lang) if t("validation_title", self.lang) != "validation_title" else "Validation",
                                t("enter_password_warning", self.lang) if t("enter_password_warning", self.lang) != "enter_password_warning" else "Please enter your password.")
            self.input_pass.setFocus()
            return

        # fetch current user
        try:
            current = get_current_user()
        except Exception as exc:
            QMessageBox.critical(self, t("error", self.lang) if t("error", self.lang) != "error" else "Error",
                                 (t("failed_read_current_user", self.lang) if t("failed_read_current_user", self.lang) != "failed_read_current_user"
                                  else f"Failed to read current user:\n{exc}"))
            self._result = False
            self.reject()
            return

        if not current:
            QMessageBox.critical(self, t("error", self.lang) if t("error", self.lang) != "error" else "Error",
                                 t("no_current_user", self.lang) if t("no_current_user", self.lang) != "no_current_user" else "No current user is set. Please login first.")
            self._result = False
            self.reject()
            return

        username = current.get("username")
        if not username:
            QMessageBox.critical(self, t("error", self.lang) if t("error", self.lang) != "error" else "Error",
                                 t("no_current_user", self.lang) if t("no_current_user", self.lang) != "no_current_user" else "No current user is set. Please login first.")
            self._result = False
            self.reject()
            return

        # attempt authentication
        try:
            auth_user = authenticate(username, pw)
        except Exception as exc:
            QMessageBox.critical(self, t("auth_error", self.lang) if t("auth_error", self.lang) != "auth_error" else "Authentication error",
                                 (t("auth_error_detail", self.lang) if t("auth_error_detail", self.lang) != "auth_error_detail"
                                  else f"Authentication error:\n{exc}"))
            self._result = False
            self.reject()
            return

        if auth_user:
            # success
            self._result = True
            self.accept()
            return
        else:
            # failed attempt
            self._attempts_left -= 1
            if self._attempts_left <= 0:
                QMessageBox.warning(self, t("auth_failed", self.lang) if t("auth_failed", self.lang) != "auth_failed" else "Authentication failed",
                                    t("invalid_password_no_attempts", self.lang) if t("invalid_password_no_attempts", self.lang) != "invalid_password_no_attempts" else "Invalid password. No attempts left.")
                self._result = False
                self.reject()
                return
            else:
                feedback = (t("invalid_password_attempts", self.lang) if t("invalid_password_attempts", self.lang) != "invalid_password_attempts"
                            else "Invalid password. Attempts left: {n}").format(n=self._attempts_left)
                self.lbl_feedback.setText(feedback)
                self.input_pass.clear()
                self.input_pass.setFocus()
                return

    # Public helper
    def exec_confirm(self) -> bool:
        """
        Run the dialog and return True if password confirmed, False otherwise.
        """
        self._attempts_left = max(1, self._attempts_left)
        self.input_pass.clear()
        self.lbl_feedback.clear()
        # Ensure the latest language is used if language_manager exists
        try:
            app = QApplication.instance()
            lm = getattr(app, "language_manager", None)
            if lm is not None and hasattr(lm, "current"):
                self.lang = lm.current
        except Exception:
            pass
        return bool(self.exec() and self._result)
