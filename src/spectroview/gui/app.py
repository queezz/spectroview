"""Application entry for the spectroview GUI."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from spectroview.gui.main_window import MainWindow
from spectroview.io import open_cube


def run_gui(path: Path | None) -> int:
    app = QApplication(sys.argv)
    if path is not None:
        cube = open_cube(path)
        window = MainWindow(cube)
    else:
        window = MainWindow()
    window.show()
    return app.exec()
