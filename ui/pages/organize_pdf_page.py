import os

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QTransform
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from tools.pdf_organize import get_page_count, reorder_pdf
from ui import icons as icon_lib
from ui.components.buttons import AnimatedButton, ProcessingBar
from ui.components.feedback import CompletionDialog
from ui.components.pdf_preview import render_pdf_page_thumbnail
from ui.components.workspace import DropWorkspace

EXTENSIONS = (".pdf",)
_ACCENT = "#ef4444"
_ICON_MUTED = "#9397a8"
THUMB_SIZE = 130


class OrganizePdfPage(QWidget):
    """Reorder, rotate, or delete pages via a drag-and-drop thumbnail grid."""

    def __init__(self, notify, parent=None):
        super().__init__(parent)

        self.notify = notify
        self.input_path = None
        self._last_output_folder = None

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
            subtitle="Drag & drop a PDF, or click to browse",
            hint="PDF",
        )
        self.drop_workspace.filesDropped.connect(lambda paths: self.load_pdf(paths[0]))
        self.drop_workspace.browseRequested.connect(self.select_pdf)
        main_layout.addWidget(self.drop_workspace)

        note = QLabel("Drag pages to reorder them. Select one or more to rotate or delete.")
        note.setObjectName("toolDescription")
        note.setWordWrap(True)
        note.hide()
        self.note_label = note
        main_layout.addWidget(note)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        self.rotate_left_button = self._toolbar_button("rotate-cw", "Rotate Left")
        self.rotate_left_button.clicked.connect(lambda: self._rotate_selected(-90))
        toolbar.addWidget(self.rotate_left_button)

        self.rotate_right_button = self._toolbar_button("rotate-cw", "Rotate Right")
        self.rotate_right_button.clicked.connect(lambda: self._rotate_selected(90))
        toolbar.addWidget(self.rotate_right_button)

        self.delete_button = self._toolbar_button("trash", "Delete Selected")
        self.delete_button.clicked.connect(self._delete_selected)
        toolbar.addWidget(self.delete_button)

        toolbar.addStretch()
        main_layout.addLayout(toolbar)

        self.page_list = QListWidget()
        self.page_list.setObjectName("organizeList")
        self.page_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.page_list.setMovement(QListWidget.Movement.Snap)
        self.page_list.setFlow(QListWidget.Flow.LeftToRight)
        self.page_list.setWrapping(True)
        self.page_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.page_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.page_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.page_list.setIconSize(QSize(THUMB_SIZE, int(THUMB_SIZE * 1.3)))
        self.page_list.setSpacing(10)
        self.page_list.setMinimumHeight(280)
        main_layout.addWidget(self.page_list)

        self.apply_button = AnimatedButton("Save Changes")
        self.apply_button.setObjectName("toolButton")
        self.apply_button.setMinimumHeight(45)
        self.apply_button.setEnabled(False)
        self.apply_button.clicked.connect(self.apply)
        main_layout.addWidget(self.apply_button)

        self.processing_bar = ProcessingBar()
        main_layout.addWidget(self.processing_bar)

        main_layout.addStretch()

        self._set_toolbar_enabled(False)

    def _toolbar_button(self, icon_name, label):
        button = QPushButton(label)
        button.setObjectName("secondaryButton")
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setIcon(icon_lib.get_icon(icon_name, _ICON_MUTED, 15))
        return button

    def _set_toolbar_enabled(self, enabled):
        self.rotate_left_button.setEnabled(enabled)
        self.rotate_right_button.setEnabled(enabled)
        self.delete_button.setEnabled(enabled)

    def select_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
        if file_path:
            self.load_pdf(file_path)

    def load_pdf(self, file_path):

        try:
            page_count = get_page_count(file_path)
        except Exception as error:
            CompletionDialog.error(self, "Unable to Open PDF", str(error))
            return

        self.input_path = file_path
        self.page_list.clear()

        for index in range(page_count):
            pixmap = render_pdf_page_thumbnail(file_path, index, THUMB_SIZE * 2)
            item = QListWidgetItem(f"Page {index + 1}")
            if pixmap is not None:
                item.setIcon(QIcon(pixmap))
            item.setData(Qt.ItemDataRole.UserRole, {"original_index": index, "rotation": 0})
            self.page_list.addItem(item)

        self.note_label.show()
        self._set_toolbar_enabled(True)
        self.apply_button.setEnabled(True)
        self.drop_workspace.set_text(os.path.basename(file_path), "Drop a different PDF or click to replace")

    def _rotate_selected(self, angle):
        for item in self.page_list.selectedItems():
            data = item.data(Qt.ItemDataRole.UserRole)
            data["rotation"] = (data["rotation"] + angle) % 360
            item.setData(Qt.ItemDataRole.UserRole, data)

            icon = item.icon()
            if not icon.isNull():
                pixmap = icon.pixmap(icon.availableSizes()[0]) if icon.availableSizes() else None
                if pixmap is not None:
                    rotated = pixmap.transformed(QTransform().rotate(angle), Qt.TransformationMode.SmoothTransformation)
                    item.setIcon(QIcon(rotated))

    def _delete_selected(self):
        for item in self.page_list.selectedItems():
            self.page_list.takeItem(self.page_list.row(item))

    def apply(self):

        if not self.input_path:
            CompletionDialog.warn(self, "No PDF Selected", "Please select a PDF first.")
            return

        if self.page_list.count() == 0:
            CompletionDialog.warn(self, "No Pages Left", "At least one page must remain.")
            return

        page_order = []
        rotations = {}
        for row in range(self.page_list.count()):
            data = self.page_list.item(row).data(Qt.ItemDataRole.UserRole)
            page_order.append(data["original_index"])
            if data["rotation"]:
                rotations[data["original_index"]] = data["rotation"]

        self.apply_button.set_processing(True, "Saving…")
        self.processing_bar.show()
        QApplication.processEvents()

        try:
            output_path = reorder_pdf(self.input_path, page_order, rotations)
            self._last_output_folder = os.path.dirname(output_path)

            self.apply_button.set_processing(False)
            self.processing_bar.hide()

            CompletionDialog.success(
                self,
                "Processing complete",
                "PDF organized successfully.",
                open_folder=self._open_output_folder,
            )

        except Exception as error:
            self.apply_button.set_processing(False)
            self.processing_bar.hide()
            CompletionDialog.error(self, "Processing Failed", f"Unable to save changes.\n\n{error}")

    def _open_output_folder(self):
        if self._last_output_folder and os.path.isdir(self._last_output_folder):
            os.startfile(self._last_output_folder)
