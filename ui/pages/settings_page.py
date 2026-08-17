from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

import settings_store
from ui.components.buttons import AnimatedButton
from ui.components.inputs import NumberField, SegmentedControl
from version import APP_VERSION

THEME_OPTIONS = [
    ("System", settings_store.THEME_SYSTEM),
    ("Light", settings_store.THEME_LIGHT),
    ("Dark", settings_store.THEME_DARK),
]

DEFAULT_FOLDER_LABEL = "Desktop\\Image & PDF Toolkit (default)"


class SettingsPage(QWidget):

    def __init__(self, notify, on_theme_changed, parent=None):
        super().__init__(parent)

        self.notify = notify
        self.on_theme_changed = on_theme_changed

        self.setup_ui()

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 15, 0, 0)
        main_layout.setSpacing(16)

        main_layout.addWidget(self._build_appearance_card())
        main_layout.addWidget(self._build_files_card())
        main_layout.addWidget(self._build_processing_card())
        main_layout.addWidget(self._build_about_card())
        main_layout.addStretch()

    # =========================
    # APPEARANCE
    # =========================

    def _build_appearance_card(self):

        card = QFrame()
        card.setObjectName("toolCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        title = QLabel("Appearance")
        title.setObjectName("toolTitle")
        layout.addWidget(title)

        description = QLabel(
            "Choose how FileForge Toolkit looks. \"System\" follows your "
            "Windows light/dark setting automatically."
        )
        description.setObjectName("toolDescription")
        description.setWordWrap(True)
        layout.addWidget(description)

        theme_label = QLabel("Theme")
        theme_label.setObjectName("fieldLabel")
        layout.addWidget(theme_label)

        current_mode = settings_store.get_theme_mode()
        current_index = next(
            (i for i, (_label, value) in enumerate(THEME_OPTIONS) if value == current_mode), 0
        )

        self.theme_control = SegmentedControl(
            [label for label, _value in THEME_OPTIONS], current_index=current_index
        )
        self.theme_control.currentChanged.connect(self.change_theme)

        control_row = QHBoxLayout()
        control_row.addWidget(self.theme_control)
        control_row.addStretch()
        layout.addLayout(control_row)

        return card

    def change_theme(self, index):

        _label, value = THEME_OPTIONS[index]
        settings_store.set_theme_mode(value)

        if self.on_theme_changed:
            self.on_theme_changed()

    # =========================
    # FILES
    # =========================

    def _build_files_card(self):

        card = QFrame()
        card.setObjectName("toolCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        title = QLabel("Files")
        title.setObjectName("toolTitle")
        layout.addWidget(title)

        description = QLabel("Converted and processed files are saved here.")
        description.setObjectName("toolDescription")
        description.setWordWrap(True)
        layout.addWidget(description)

        self.folder_label = QLabel()
        self.folder_label.setObjectName("toolDescription")
        self.folder_label.setWordWrap(True)
        self.refresh_folder_label()
        layout.addWidget(self.folder_label)

        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(10)

        change_button = AnimatedButton("Change Folder")
        change_button.setObjectName("toolButton")
        change_button.clicked.connect(self.change_folder)
        buttons_row.addWidget(change_button)

        reset_button = AnimatedButton("Reset to Default")
        reset_button.setObjectName("secondaryButton")
        reset_button.clicked.connect(self.reset_folder)
        buttons_row.addWidget(reset_button)
        buttons_row.addStretch()

        layout.addLayout(buttons_row)

        return card

    def refresh_folder_label(self):

        custom_folder = settings_store.get_output_folder()
        self.folder_label.setText(custom_folder if custom_folder else DEFAULT_FOLDER_LABEL)

    def change_folder(self):

        start_dir = settings_store.get_output_folder() or str(Path.home() / "Desktop")

        folder = QFileDialog.getExistingDirectory(self, "Choose Save Folder", start_dir)

        if not folder:
            return

        settings_store.set_output_folder(folder)
        self.refresh_folder_label()
        self.notify(f"Files will now be saved to {folder}")

    def reset_folder(self):

        settings_store.reset_output_folder()
        self.refresh_folder_label()
        self.notify("Save location reset to the default folder")

    # =========================
    # PROCESSING
    # =========================

    def _build_processing_card(self):

        card = QFrame()
        card.setObjectName("toolCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(16)

        title = QLabel("Processing")
        title.setObjectName("toolTitle")
        layout.addWidget(title)

        description = QLabel(
            "Starting values for Image Resizer — you can always adjust them "
            "per-image before compressing."
        )
        description.setObjectName("toolDescription")
        description.setWordWrap(True)
        layout.addWidget(description)

        options_row = QHBoxLayout()
        options_row.setSpacing(28)

        self.default_target_field = NumberField(
            "Default Target Size", 5, 5000, settings_store.get_default_target_kb(), suffix=" KB"
        )
        self.default_target_field.valueChanged.connect(settings_store.set_default_target_kb)

        self.default_quality_field = NumberField(
            "Default Maximum Quality", 5, 100, settings_store.get_default_quality(), suffix="%"
        )
        self.default_quality_field.valueChanged.connect(settings_store.set_default_quality)

        options_row.addWidget(self.default_target_field)
        options_row.addWidget(self.default_quality_field)
        layout.addLayout(options_row)

        return card

    # =========================
    # ABOUT
    # =========================

    def _build_about_card(self):

        card = QFrame()
        card.setObjectName("toolCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(6)

        title = QLabel("About")
        title.setObjectName("toolTitle")
        layout.addWidget(title)

        layout.addSpacing(4)

        rows = [
            ("Application", "FileForge Toolkit"),
            ("Version", f"v{APP_VERSION}"),
            ("License", "MIT License"),
            ("Created by", "Rahul Swargam"),
        ]

        for label_text, value_text in rows:
            row = QHBoxLayout()
            label = QLabel(label_text)
            label.setObjectName("fieldLabel")
            value = QLabel(value_text)
            value.setObjectName("toolDescription")
            row.addWidget(label)
            row.addStretch()
            row.addWidget(value)
            layout.addLayout(row)

        return card
