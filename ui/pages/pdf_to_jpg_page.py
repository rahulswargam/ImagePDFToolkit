import os

from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from tools.pdf_to_jpg import convert_pdf_to_jpg
from ui.widgets import AnimatedButton, DropArea

EXTENSIONS = (".pdf",)
MAX_QUALITY = 100
MAX_DPI = 600


class PdfToJpgPage(QWidget):

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

        self.output_folder_label = QLabel("Output: Desktop\\Image & PDF Toolkit\\<pdf name>")
        self.output_folder_label.setObjectName("toolDescription")
        self.output_folder_label.setWordWrap(True)

        info_layout.addWidget(select_button)
        info_layout.addWidget(self.file_label)
        info_layout.addStretch()
        info_layout.addWidget(self.output_folder_label)

        file_layout.addLayout(info_layout)

        main_layout.addWidget(file_card)

        note = QLabel("Pages are exported at maximum quality and resolution (600 DPI).")
        note.setObjectName("toolDescription")
        note.setWordWrap(True)
        main_layout.addWidget(note)

        convert_button = AnimatedButton("Convert to JPG")
        convert_button.setObjectName("toolButton")
        convert_button.setMinimumHeight(45)
        convert_button.clicked.connect(self.convert)

        main_layout.addWidget(convert_button)
        main_layout.addStretch()

    def select_pdf(self):

        file_path, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")

        if file_path:
            self.load_pdf(file_path)

    def load_pdf(self, file_path):

        self.input_path = file_path
        self.file_label.setText(os.path.basename(file_path))
        self.drop_area.setText(os.path.basename(file_path))

    def convert(self):

        if not self.input_path:
            QMessageBox.warning(self, "No PDF", "Please select a PDF first.")
            return

        try:
            output_paths = convert_pdf_to_jpg(self.input_path, MAX_QUALITY, MAX_DPI)

            folder = os.path.dirname(output_paths[0])
            self.notify(f"Saved {len(output_paths)} page(s) to {folder}")

        except Exception as error:
            QMessageBox.critical(self, "Error", f"Could not convert PDF.\n\n{error}")
