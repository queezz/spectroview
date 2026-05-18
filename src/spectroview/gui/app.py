"""Application entry for the spectroview GUI."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from spectroview.gui.main_window import MainWindow
from spectroview.io import open_cube


def run_gui(path: Path) -> int:
    cube = open_cube(path)
    app = QApplication(sys.argv)
    window = MainWindow(cube)
    window.show()
    return app.exec()
