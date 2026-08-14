import os
from pathlib import Path

from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

import settings_store
from ui.widgets import AnimatedButton

THEME_OPTIONS = [
    ("System Default", settings_store.THEME_SYSTEM),
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
        main_layout.setSpacing(15)

        # =========================
        # APPEARANCE
        # =========================

        appearance_card = QFrame()
        appearance_card.setObjectName("toolCard")

        appearance_layout = QVBoxLayout(appearance_card)
        appearance_layout.setContentsMargins(20, 18, 20, 18)
        appearance_layout.setSpacing(12)

        appearance_title = QLabel("Appearance")
        appearance_title.setObjectName("toolTitle")
        appearance_layout.addWidget(appearance_title)

        appearance_description = QLabel(
            "Choose how Image & PDF Toolkit looks. \"System Default\" follows "
            "your Windows light/dark setting automatically."
        )
        appearance_description.setObjectName("toolDescription")
        appearance_description.setWordWrap(True)
        appearance_layout.addWidget(appearance_description)

        theme_label = QLabel("Theme")
        theme_label.setObjectName("fieldLabel")
        appearance_layout.addWidget(theme_label)

        self.theme_combo = QComboBox()
        self.theme_combo.setMinimumHeight(40)
        for label, _value in THEME_OPTIONS:
            self.theme_combo.addItem(label)

        current_mode = settings_store.get_theme_mode()
        for index, (_label, value) in enumerate(THEME_OPTIONS):
            if value == current_mode:
                self.theme_combo.setCurrentIndex(index)
                break

        self.theme_combo.currentIndexChanged.connect(self.change_theme)
        appearance_layout.addWidget(self.theme_combo)

        main_layout.addWidget(appearance_card)

        # =========================
        # DEFAULT SAVE LOCATION
        # =========================

        folder_card = QFrame()
        folder_card.setObjectName("toolCard")

        folder_layout = QVBoxLayout(folder_card)
        folder_layout.setContentsMargins(20, 18, 20, 18)
        folder_layout.setSpacing(12)

        folder_title = QLabel("Default Save Location")
        folder_title.setObjectName("toolTitle")
        folder_layout.addWidget(folder_title)

        folder_description = QLabel("Converted and processed files are saved here.")
        folder_description.setObjectName("toolDescription")
        folder_description.setWordWrap(True)
        folder_layout.addWidget(folder_description)

        self.folder_label = QLabel()
        self.folder_label.setObjectName("toolDescription")
        self.folder_label.setWordWrap(True)
        self.refresh_folder_label()
        folder_layout.addWidget(self.folder_label)

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

        folder_layout.addLayout(buttons_row)

        main_layout.addWidget(folder_card)
        main_layout.addStretch()

    def refresh_folder_label(self):

        custom_folder = settings_store.get_output_folder()

        if custom_folder:
            self.folder_label.setText(custom_folder)
        else:
            self.folder_label.setText(DEFAULT_FOLDER_LABEL)

    def change_theme(self, index):

        _label, value = THEME_OPTIONS[index]
        settings_store.set_theme_mode(value)

        if self.on_theme_changed:
            self.on_theme_changed()

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
