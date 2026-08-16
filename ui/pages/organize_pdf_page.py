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

from tools.pdf_organize import get_page_count, reorder_multi_pdf
from ui import icons as icon_lib
from ui.components.buttons import AnimatedButton, ProcessingBar
from ui.components.feedback import CompletionDialog
from ui.components.pdf_preview import render_pdf_page_thumbnail
from ui.components.workspace import MAX_BATCH_FILES, DropWorkspace, clip_to_max_files

EXTENSIONS = (".pdf",)
_ACCENT = "#ef4444"
_ICON_MUTED = "#9397a8"
THUMB_SIZE = 130
# The grid cell must be larger than the icon alone to leave room for the
# QSS item border/padding and the two-line label Qt draws below the icon
# in IconMode. Without an explicit, uniform grid, Qt's per-item layout
# drifts (items visually overlap/jump) because the stylesheet's box model
# isn't reflected in Qt's own size-hint math for IconMode cells.
GRID_CELL_WIDTH = THUMB_SIZE + 40
GRID_CELL_HEIGHT = int(THUMB_SIZE * 1.3) + 80


class OrganizePdfPage(QWidget):
    """Reorder, rotate, or delete pages — across up to MAX_BATCH_FILES PDFs
    combined into one thumbnail grid — via explicit Move Left/Right
    controls rather than a live drag gesture.

    An earlier version used QListWidget's native IconMode drag-and-drop
    (InternalMove) for reordering. That has a real, reproducible Qt layout
    bug in this app's widget hierarchy (the list is nested inside the
    page's own scroll area): after a drop, items can render overlapping or
    with stale gaps at their former position, even with a fixed uniform
    grid size. Move buttons perform the exact same underlying operation
    (takeItem + insertItem) but outside of any live-drag paint loop, which
    sidesteps that bug entirely — confirmed correct by test.
    """

    def __init__(self, notify, parent=None):
        super().__init__(parent)

        self.notify = notify
        self.loaded_paths = []
        self._last_output_path = None

        self.setup_ui()

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 15, 0, 0)
        main_layout.setSpacing(16)

        self.drop_workspace = DropWorkspace(
            EXTENSIONS,
            _ACCENT,
            multiple=True,
            title="Drop PDFs here",
            subtitle=f"Drag & drop up to {MAX_BATCH_FILES} PDFs, or click to browse",
            hint="PDF",
        )
        self.drop_workspace.filesDropped.connect(self.load_pdfs)
        self.drop_workspace.browseRequested.connect(self.select_pdfs)
        main_layout.addWidget(self.drop_workspace)

        note = QLabel("Select a page, then use Move Left/Right to reorder it. Select one or more to rotate or delete.")
        note.setObjectName("toolDescription")
        note.setWordWrap(True)
        note.hide()
        self.note_label = note
        main_layout.addWidget(note)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        self.move_left_button = self._toolbar_button("chevron-left", "Move Left")
        self.move_left_button.clicked.connect(lambda: self._move_selected(-1))
        toolbar.addWidget(self.move_left_button)

        self.move_right_button = self._toolbar_button("chevron-right", "Move Right")
        self.move_right_button.clicked.connect(lambda: self._move_selected(1))
        toolbar.addWidget(self.move_right_button)

        toolbar.addSpacing(12)

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
        self.page_list.setMovement(QListWidget.Movement.Static)
        self.page_list.setFlow(QListWidget.Flow.LeftToRight)
        self.page_list.setWrapping(True)
        self.page_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.page_list.setDragDropMode(QAbstractItemView.DragDropMode.NoDragDrop)
        self.page_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.page_list.setIconSize(QSize(THUMB_SIZE, int(THUMB_SIZE * 1.3)))
        self.page_list.setUniformItemSizes(True)
        self.page_list.setGridSize(QSize(GRID_CELL_WIDTH, GRID_CELL_HEIGHT))
        self.page_list.setSpacing(0)
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
        self.move_left_button.setEnabled(enabled)
        self.move_right_button.setEnabled(enabled)
        self.rotate_left_button.setEnabled(enabled)
        self.rotate_right_button.setEnabled(enabled)
        self.delete_button.setEnabled(enabled)

    def select_pdfs(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select PDFs", "", "PDF Files (*.pdf)")
        if file_paths:
            self.load_pdfs(file_paths)

    def load_pdfs(self, file_paths):

        file_paths, truncated = clip_to_max_files(list(self.loaded_paths) + list(file_paths))
        new_paths = [path for path in file_paths if path not in self.loaded_paths]

        for file_path in new_paths:
            try:
                page_count = get_page_count(file_path)
            except Exception as error:
                CompletionDialog.error(self, "Unable to Open PDF", f"{os.path.basename(file_path)}: {error}")
                continue

            self.loaded_paths.append(file_path)
            label_stem = os.path.splitext(os.path.basename(file_path))[0]

            for index in range(page_count):
                pixmap = render_pdf_page_thumbnail(file_path, index, THUMB_SIZE * 2)
                item = QListWidgetItem(f"{label_stem}\np{index + 1}")
                if pixmap is not None:
                    item.setIcon(QIcon(pixmap))
                item.setData(Qt.ItemDataRole.UserRole, {"source_path": file_path, "page_index": index, "rotation": 0})
                self.page_list.addItem(item)

        if truncated:
            CompletionDialog.warn(
                self,
                "Too Many PDFs",
                f"Only the first {MAX_BATCH_FILES} PDFs were kept "
                f"({truncated} extra file(s) were not added).",
            )

        has_pages = self.page_list.count() > 0
        self.note_label.setVisible(has_pages)
        self._set_toolbar_enabled(has_pages)
        self.apply_button.setEnabled(has_pages)

        plural = "PDF" if len(self.loaded_paths) == 1 else "PDFs"
        if self.loaded_paths:
            self.drop_workspace.set_text(
                f"{len(self.loaded_paths)} {plural} loaded", "Drop more PDFs or click to add"
            )

    def _move_selected(self, direction):
        selected = self.page_list.selectedItems()

        if len(selected) != 1:
            CompletionDialog.warn(self, "Select One Page", "Select exactly one page to move.")
            return

        item = selected[0]
        row = self.page_list.row(item)
        new_row = row + direction

        if new_row < 0 or new_row >= self.page_list.count():
            return

        self.page_list.takeItem(row)
        self.page_list.insertItem(new_row, item)
        item.setSelected(True)
        self.page_list.setCurrentItem(item)

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

        has_pages = self.page_list.count() > 0
        self._set_toolbar_enabled(has_pages)
        self.apply_button.setEnabled(has_pages)

    def apply(self):

        if self.page_list.count() == 0:
            CompletionDialog.warn(self, "No Pages Left", "At least one page must remain.")
            return

        page_entries = []
        rotations = {}
        for row in range(self.page_list.count()):
            data = self.page_list.item(row).data(Qt.ItemDataRole.UserRole)
            key = (data["source_path"], data["page_index"])
            page_entries.append(key)
            if data["rotation"]:
                rotations[key] = data["rotation"]

        output_name = (
            os.path.splitext(os.path.basename(self.loaded_paths[0]))[0] if self.loaded_paths else "organized"
        )

        self.apply_button.set_processing(True, "Saving…")
        self.processing_bar.show()
        QApplication.processEvents()

        try:
            output_path = reorder_multi_pdf(page_entries, rotations, output_name)
            self._last_output_path = output_path

            self.apply_button.set_processing(False)
            self.processing_bar.hide()

            CompletionDialog.success(
                self,
                "Processing complete",
                "PDF organized successfully.",
                open_file=self._open_output_file,
            )

        except Exception as error:
            self.apply_button.set_processing(False)
            self.processing_bar.hide()
            CompletionDialog.error(self, "Processing Failed", f"Unable to save changes.\n\n{error}")

    def _open_output_file(self):
        if self._last_output_path and os.path.isfile(self._last_output_path):
            os.startfile(self._last_output_path)
