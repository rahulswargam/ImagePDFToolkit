import os

from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from tools.unlock_pdf import unlock_pdf
from ui.widgets import AnimatedButton, DropArea, RevealButton

EXTENSIONS = (".pdf",)


class UnlockPdfPage(QWidget):

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
            placeholder="Drag & drop a locked PDF here\nor click Select PDF",
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

        settings_title = QLabel("Current Password")
        settings_title.setObjectName("toolTitle")
        settings_layout.addWidget(settings_title)

        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Password")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)

        reveal_button = RevealButton(self.password_edit)
        reveal_button.setFixedWidth(72)
        reveal_button.setToolTip("Hold to show the password")

        password_row = QHBoxLayout()
        password_row.setSpacing(10)
        password_row.addWidget(self.password_edit)
        password_row.addWidget(reveal_button)

        settings_layout.addLayout(password_row)

        main_layout.addWidget(settings_card)

        unlock_button = AnimatedButton("Unlock PDF")
        unlock_button.setObjectName("toolButton")
        unlock_button.setMinimumHeight(45)
        unlock_button.clicked.connect(self.unlock)

        main_layout.addWidget(unlock_button)
        main_layout.addStretch()

    def select_pdf(self):

        file_path, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")

        if file_path:
            self.load_pdf(file_path)

    def load_pdf(self, file_path):

        self.input_path = file_path
        self.file_label.setText(os.path.basename(file_path))
        self.drop_area.setText(os.path.basename(file_path))

    def unlock(self):

        if not self.input_path:
            QMessageBox.warning(self, "No PDF", "Please select a PDF first.")
            return

        try:
            output_path = unlock_pdf(self.input_path, self.password_edit.text())
            self.notify(f"Saved to {output_path}")

            self.password_edit.clear()

        except Exception as error:
            QMessageBox.critical(self, "Error", f"Could not unlock PDF.\n\n{error}")
