"""Application entry for the spectroview GUI."""

from __future__ import annotations

import sys
from importlib.resources import as_file, files
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from spectroview.gui.main_window import MainWindow
from spectroview.io import open_cube


def application_icon() -> QIcon:
    icon_resource = files("spectroview").joinpath("assets/spectrocube_icon.svg")
    with as_file(icon_resource) as icon_path:
        return QIcon(str(icon_path))


def run_gui(path: Path | None) -> int:
    app = QApplication(sys.argv)
    app.setWindowIcon(application_icon())
    if path is not None:
        cube = open_cube(path)
        window = MainWindow(cube)
    else:
        window = MainWindow()
    window.setWindowIcon(app.windowIcon())
    window.show()
    return app.exec()
