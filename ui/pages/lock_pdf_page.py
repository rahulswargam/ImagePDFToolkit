import os

from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from tools.lock_pdf import lock_pdf
from ui.widgets import AnimatedButton, DropArea, RevealButton

EXTENSIONS = (".pdf",)


class LockPdfPage(QWidget):

    def __init__(self, notify, parent=None):
        super().__init__(parent)

        self.notify = notify
        self.input_path = None

        self.setup_ui()

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 15, 0, 0)
        main_layout.setSpacing(15)

        file_card = QFrame()
        file_card.setObjectName("toolCard")

        file_layout = QHBoxLayout(file_card)
        file_layout.setContentsMargins(20, 20, 20, 20)
        file_layout.setSpacing(20)

        self.drop_area = DropArea(
            EXTENSIONS,
            multiple=False,
            placeholder="Drag & drop a PDF here\nor click Select PDF",
        )
        self.drop_area.setFixedSize(280, 210)
        self.drop_area.filesDropped.connect(lambda paths: self.load_pdf(paths[0]))

        file_layout.addWidget(self.drop_area)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(10)

        select_button = AnimatedButton("Select PDF")
        select_button.setObjectName("toolButton")
        select_button.clicked.connect(self.select_pdf)

        self.file_label = QLabel("No PDF selected")
        self.file_label.setObjectName("toolDescription")
        self.file_label.setWordWrap(True)

        self.output_folder_label = QLabel("Output: Desktop\\Image & PDF Toolkit")
        self.output_folder_label.setObjectName("toolDescription")
        self.output_folder_label.setWordWrap(True)

        info_layout.addWidget(select_button)
        info_layout.addWidget(self.file_label)
        info_layout.addStretch()
        info_layout.addWidget(self.output_folder_label)

        file_layout.addLayout(info_layout)

        main_layout.addWidget(file_card)

        settings_card = QFrame()
        settings_card.setObjectName("toolCard")

        settings_layout = QVBoxLayout(settings_card)
        settings_layout.setContentsMargins(20, 18, 20, 18)
        settings_layout.setSpacing(12)

        settings_title = QLabel("Set Password")
        settings_title.setObjectName("toolTitle")
        settings_layout.addWidget(settings_title)

        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Password")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)

        self.confirm_edit = QLineEdit()
        self.confirm_edit.setPlaceholderText("Confirm password")
        self.confirm_edit.setEchoMode(QLineEdit.EchoMode.Password)

        reveal_button = RevealButton([self.password_edit, self.confirm_edit])
        reveal_button.setFixedWidth(72)
        reveal_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        reveal_button.setToolTip("Hold to show both passwords")

        fields_layout = QGridLayout()
        fields_layout.setHorizontalSpacing(10)
        fields_layout.setVerticalSpacing(10)
        fields_layout.addWidget(self.password_edit, 0, 0)
        fields_layout.addWidget(self.confirm_edit, 1, 0)
        fields_layout.addWidget(reveal_button, 0, 1, 2, 1)

        settings_layout.addLayout(fields_layout)

        main_layout.addWidget(settings_card)

        lock_button = AnimatedButton("Lock PDF")
        lock_button.setObjectName("toolButton")
        lock_button.setMinimumHeight(45)
        lock_button.clicked.connect(self.lock)

        main_layout.addWidget(lock_button)
        main_layout.addStretch()

    def select_pdf(self):

        file_path, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")

        if file_path:
            self.load_pdf(file_path)

    def load_pdf(self, file_path):

        self.input_path = file_path
        self.file_label.setText(os.path.basename(file_path))
        self.drop_area.setText(os.path.basename(file_path))

    def lock(self):

        if not self.input_path:
            QMessageBox.warning(self, "No PDF", "Please select a PDF first.")
            return

        password = self.password_edit.text()
        confirm = self.confirm_edit.text()

        if not password:
            QMessageBox.warning(self, "Missing Password", "Please enter a password.")
            return

        if password != confirm:
            QMessageBox.warning(self, "Password Mismatch", "Passwords do not match.")
            return

        try:
            output_path = lock_pdf(self.input_path, password)
            self.notify(f"Saved to {output_path}")

            self.password_edit.clear()
            self.confirm_edit.clear()

        except Exception as error:
            QMessageBox.critical(self, "Error", f"Could not lock PDF.\n\n{error}")
