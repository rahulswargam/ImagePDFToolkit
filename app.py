import os
import sys

from PySide6.QtGui import QFont, QFontDatabase, QIcon
from PySide6.QtWidgets import QApplication, QStyleFactory
from ui.main_window import MainWindow

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(BASE_DIR, "assets", "icons", "app.ico")
FONT_PATH = os.path.join(BASE_DIR, "assets", "fonts", "Roboto-Variable.ttf")


def load_app_font():
    if os.path.exists(FONT_PATH):
        QFontDatabase.addApplicationFont(FONT_PATH)


def main():
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))

    app.setApplicationName("FileForge Toolkit")

    load_app_font()
    app.setFont(QFont("Roboto", 10))

    if os.path.exists(ICON_PATH):
        app.setWindowIcon(QIcon(ICON_PATH))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
