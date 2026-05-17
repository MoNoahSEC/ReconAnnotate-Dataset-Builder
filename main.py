"""
Entry point for the Noah ReconAnnotate Pro.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt
from annotation_tool.app import MainWindow
from annotation_tool.styles.theme import get_stylesheet


def main():
    """Docstring"""
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"

    app = QApplication(sys.argv)

    app.setStyleSheet(get_stylesheet())

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    app.setApplicationName("Noah ReconAnnotate Pro")
    app.setApplicationDisplayName("Noah ReconAnnotate Pro — Premium Dataset Builder")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
