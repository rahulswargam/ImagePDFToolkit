import os

from PySide6.QtWidgets import QApplication, QCheckBox, QFileDialog, QFrame, QLabel, QVBoxLayout, QWidget

from tools.pdf_forms import fill_form, get_form_fields
from ui.components.buttons import AnimatedButton, ProcessingBar
from ui.components.feedback import CompletionDialog
from ui.components.inputs import LabeledLineEdit
from ui.components.pdf_preview import PdfPreviewCard
from ui.components.workspace import DropWorkspace

EXTENSIONS = (".pdf",)
_ACCENT = "#ef4444"


class PdfFormsPage(QWidget):
    """Detects a PDF's fillable AcroForm fields and lets you fill them in."""

    def __init__(self, notify, parent=None):
        super().__init__(parent)

        self.notify = notify
        self.input_path = None
        self._last_output_path = None
        self._preview_card = None
        self._field_widgets = {}

        self.setup_ui()

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 15, 0, 0)
        main_layout.setSpacing(16)

        self.drop_workspace = DropWorkspace(
            EXTENSIONS,
            _ACCENT,
            multiple=False,
            title="Drop a PDF here",
            subtitle="Drag & drop a fillable PDF form, or click to browse",
            hint="PDF",
        )
        self.drop_workspace.filesDropped.connect(lambda paths: self.load_pdf(paths[0]))
        self.drop_workspace.browseRequested.connect(self.select_pdf)
        main_layout.addWidget(self.drop_workspace)

        self.preview_container = QVBoxLayout()
        main_layout.addLayout(self.preview_container)

        self.form_container = QVBoxLayout()
        main_layout.addLayout(self.form_container)

        self.save_button = AnimatedButton("Save Filled PDF")
        self.save_button.setObjectName("toolButton")
        self.save_button.setMinimumHeight(45)
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save)
        main_layout.addWidget(self.save_button)

        self.processing_bar = ProcessingBar()
        main_layout.addWidget(self.processing_bar)

        main_layout.addStretch()

    def select_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
        if file_path:
            self.load_pdf(file_path)

    def load_pdf(self, file_path):

        try:
            fields = get_form_fields(file_path)
        except Exception as error:
            CompletionDialog.warn(self, "No Fillable Fields", str(error))
            return

        self.input_path = file_path
        self.save_button.setEnabled(True)

        if self._preview_card is not None:
            self._preview_card.setParent(None)
            self._preview_card.deleteLater()

        self._preview_card = PdfPreviewCard(file_path)
        self._preview_card.removed.connect(self._clear_pdf)
        self.preview_container.addWidget(self._preview_card)

        self._build_form(fields)
        self.drop_workspace.set_text(os.path.basename(file_path), "Drop a different PDF or click to replace")

    def _build_form(self, fields):

        while self.form_container.count():
            item = self.form_container.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self._field_widgets = {}

        card = QFrame()
        card.setObjectName("toolCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(14)

        title = QLabel(f"Form Fields ({len(fields)})")
        title.setObjectName("toolTitle")
        card_layout.addWidget(title)

        for field in fields:
            if field["type"] == "text":
                widget = LabeledLineEdit(field["name"])
                widget.setText(field["value"])
                card_layout.addWidget(widget)
                self._field_widgets[field["name"]] = ("text", widget)
            else:
                checkbox = QCheckBox(field["name"])
                checkbox.setChecked(bool(field["value"]))
                card_layout.addWidget(checkbox)
                self._field_widgets[field["name"]] = ("checkbox", checkbox)

        self.form_container.addWidget(card)

    def _clear_pdf(self):
        self.input_path = None
        self.save_button.setEnabled(False)
        self._field_widgets = {}

        if self._preview_card is not None:
            self._preview_card.setParent(None)
            self._preview_card.deleteLater()
            self._preview_card = None

        while self.form_container.count():
            item = self.form_container.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.drop_workspace.set_text("Drop a PDF here", "Drag & drop a fillable PDF form, or click to browse")

    def save(self):

        if not self.input_path or not self._field_widgets:
            CompletionDialog.warn(self, "No PDF Selected", "Please select a fillable PDF first.")
            return

        values = {}
        for name, (kind, widget) in self._field_widgets.items():
            values[name] = widget.text() if kind == "text" else widget.isChecked()

        self.save_button.set_processing(True, "Saving…")
        self.processing_bar.show()
        QApplication.processEvents()

        try:
            output_path = fill_form(self.input_path, values)
            self._last_output_path = output_path

            self.save_button.set_processing(False)
            self.processing_bar.hide()

            CompletionDialog.success(
                self,
                "Processing complete",
                "Form filled and saved successfully.",
                open_file=self._open_output_file,
            )

        except Exception as error:
            self.save_button.set_processing(False)
            self.processing_bar.hide()
            CompletionDialog.error(self, "Processing Failed", f"Unable to save this form.\n\n{error}")

    def _open_output_file(self):
        if self._last_output_path and os.path.isfile(self._last_output_path):
            os.startfile(self._last_output_path)
