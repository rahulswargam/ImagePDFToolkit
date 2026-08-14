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
from ui.widgets import MAX_BATCH_FILES, AnimatedButton, DropArea, clip_to_max_files

EXTENSIONS = (".pdf",)
MAX_QUALITY = 100
MAX_DPI = 600


class PdfToJpgPage(QWidget):

    def __init__(self, notify, parent=None):
        super().__init__(parent)

        self.notify = notify
        self.input_paths = []

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
            multiple=True,
            placeholder=f"Drag & drop up to {MAX_BATCH_FILES} PDFs here\nor click Select PDFs",
        )
        self.drop_area.setFixedSize(280, 210)
        self.drop_area.filesDropped.connect(self.load_pdfs)

        file_layout.addWidget(self.drop_area)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(10)

        select_button = AnimatedButton("Select PDFs")
        select_button.setObjectName("toolButton")
        select_button.clicked.connect(self.select_pdfs)

        self.files_label = QLabel("No PDFs selected")
        self.files_label.setObjectName("toolDescription")
        self.files_label.setWordWrap(True)

        self.output_folder_label = QLabel("Output: Desktop\\Image & PDF Toolkit\\<pdf name>")
        self.output_folder_label.setObjectName("toolDescription")
        self.output_folder_label.setWordWrap(True)

        info_layout.addWidget(select_button)
        info_layout.addWidget(self.files_label)
        info_layout.addStretch()
        info_layout.addWidget(self.output_folder_label)

        file_layout.addLayout(info_layout)

        main_layout.addWidget(file_card)

        note = QLabel(
            "Each PDF's pages are exported at maximum quality and resolution "
            "(600 DPI) into their own subfolder."
        )
        note.setObjectName("toolDescription")
        note.setWordWrap(True)
        main_layout.addWidget(note)

        convert_button = AnimatedButton("Convert to JPG")
        convert_button.setObjectName("toolButton")
        convert_button.setMinimumHeight(45)
        convert_button.clicked.connect(self.convert)

        main_layout.addWidget(convert_button)
        main_layout.addStretch()

    def select_pdfs(self):

        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Select PDFs", "", "PDF Files (*.pdf)"
        )

        if file_paths:
            self.load_pdfs(file_paths)

    def load_pdfs(self, file_paths):

        file_paths, truncated = clip_to_max_files(file_paths)

        self.input_paths = file_paths

        names = "\n".join(os.path.basename(path) for path in file_paths)
        self.files_label.setText(f"{len(file_paths)} PDF(s) selected:\n{names}")

        self.drop_area.setText(f"{len(file_paths)} PDF(s) ready")

        if truncated:
            QMessageBox.warning(
                self,
                "Too Many PDFs",
                f"Only the first {MAX_BATCH_FILES} PDFs were kept "
                f"({truncated} extra file(s) were not added).",
            )

    def convert(self):

        if not self.input_paths:
            QMessageBox.warning(self, "No PDFs", "Please select at least one PDF first.")
            return

        converted_pdfs = 0
        total_pages = 0
        failed = []
        last_output_root = None

        for input_path in self.input_paths:
            try:
                output_paths = convert_pdf_to_jpg(input_path, MAX_QUALITY, MAX_DPI)
                converted_pdfs += 1
                total_pages += len(output_paths)
                last_output_root = os.path.dirname(os.path.dirname(output_paths[0]))

            except Exception as error:
                failed.append(f"{os.path.basename(input_path)}: {error}")

        if converted_pdfs:
            pdf_plural = "PDF" if converted_pdfs == 1 else "PDFs"
            page_plural = "page" if total_pages == 1 else "pages"
            self.notify(
                f"Converted {converted_pdfs} {pdf_plural} — {total_pages} {page_plural} total, "
                f"saved to {last_output_root}"
            )

        if failed:
            QMessageBox.critical(
                self,
                "Some PDFs Failed",
                "Could not convert:\n\n" + "\n".join(failed),
            )
