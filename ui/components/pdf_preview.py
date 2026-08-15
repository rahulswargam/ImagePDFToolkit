import os

import pymupdf
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from tools.image_resizer import format_file_size
from ui import icons as icon_lib

_ICON_MUTED = "#9397a8"


def render_pdf_thumbnail(path, max_size=200):
    """Renders the first page of a PDF to a QPixmap, or None if it can't be read."""

    try:
        doc = pymupdf.open(path)
        page = doc[0]
        rect = page.rect
        zoom = max_size / max(rect.width, rect.height, 1)
        matrix = pymupdf.Matrix(zoom, zoom)
        pixmap = page.get_pixmap(matrix=matrix, alpha=False)
        image = QImage(pixmap.samples, pixmap.width, pixmap.height, pixmap.stride, QImage.Format.Format_RGB888)
        qpixmap = QPixmap.fromImage(image.copy())
        doc.close()
        return qpixmap
    except Exception:
        return None


def pdf_meta_text(path):
    try:
        size_text = format_file_size(os.path.getsize(path))
        doc = pymupdf.open(path)
        page_count = len(doc)
        doc.close()
        plural = "page" if page_count == 1 else "pages"
        return f"{page_count} {plural} · {size_text}"
    except Exception:
        return ""


class PdfPreviewCard(QFrame):
    """A single-PDF preview card: rendered first-page thumbnail, filename, meta, remove."""

    removed = Signal()

    def __init__(self, file_path, parent=None):
        super().__init__(parent)

        self.file_path = file_path
        self.setObjectName("fileGridItem")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        thumb = QLabel()
        thumb.setObjectName("fileGridThumb")
        thumb.setFixedSize(84, 108)
        thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)

        rendered = render_pdf_thumbnail(file_path, max_size=100)
        if rendered is not None:
            thumb.setPixmap(
                rendered.scaled(
                    76,
                    100,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        else:
            thumb.setPixmap(icon_lib.get_pixmap("file-text", _ICON_MUTED, 32))

        layout.addWidget(thumb)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)

        name_label = QLabel(os.path.basename(file_path))
        name_label.setObjectName("toolTitle")
        name_label.setWordWrap(True)
        text_layout.addWidget(name_label)

        meta_label = QLabel(pdf_meta_text(file_path))
        meta_label.setObjectName("fileGridMeta")
        text_layout.addWidget(meta_label)
        text_layout.addStretch()

        layout.addLayout(text_layout, 1)

        remove_button = QPushButton()
        remove_button.setObjectName("iconButton")
        remove_button.setIcon(icon_lib.get_icon("x", _ICON_MUTED, 14))
        remove_button.setIconSize(QSize(14, 14))
        remove_button.setFixedSize(28, 28)
        remove_button.setCursor(Qt.CursorShape.PointingHandCursor)
        remove_button.setToolTip(f"Remove {os.path.basename(file_path)}")
        remove_button.setAccessibleName(f"Remove {os.path.basename(file_path)}")
        remove_button.clicked.connect(self.removed.emit)
        layout.addWidget(remove_button, alignment=Qt.AlignmentFlag.AlignTop)
