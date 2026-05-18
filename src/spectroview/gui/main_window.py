"""Main spectroview window."""

from __future__ import annotations

from pathlib import Path

import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QSlider,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from spectroview.gui.quicklook_maps import QuicklookMapsPanel
from spectroview.io import open_cube
from spectroview.model import SpectroCubeViewModel
from spectroview.regions import WavelengthRegion, available_regions


class MainWindow(QMainWindow):
    def __init__(self, cube: SpectroCubeViewModel | None = None) -> None:
        super().__init__()
        self._cube: SpectroCubeViewModel | None = None
        self._quicklook: QuicklookMapsPanel | None = None

        self.setWindowTitle("SpectroView")
        self.setAcceptDrops(True)

        central = QWidget()
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)

        self._drop_hint = QLabel("Drop a SpectroCube .nc file here")
        self._drop_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._drop_hint.setStyleSheet("color: gray; font-size: 14pt; padding: 12px;")
        outer.addWidget(self._drop_hint)

        self._meta_label = QLabel("")
        self._meta_label.setWordWrap(True)
        self._meta_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._meta_label.setVisible(False)
        outer.addWidget(self._meta_label)

        slider_row = QHBoxLayout()
        slider_row.addWidget(QLabel("Frame:"))
        self._frame_slider = QSlider(Qt.Orientation.Horizontal)
        self._frame_slider.setMinimum(0)
        self._frame_slider.setMaximum(0)
        self._frame_slider.setValue(0)
        self._frame_slider.setEnabled(False)
        self._frame_slider.valueChanged.connect(self._on_frame_changed)
        slider_row.addWidget(self._frame_slider, stretch=1)
        self._frame_label = QLabel("—")
        slider_row.addWidget(self._frame_label)
        outer.addLayout(slider_row)

        region_row = QHBoxLayout()
        region_row.addWidget(QLabel("Region:"))
        self._region_combo = QComboBox()
        self._region_combo.addItem("Full spectrum", None)
        self._region_combo.setEnabled(False)
        self._region_combo.currentIndexChanged.connect(self._on_region_changed)
        region_row.addWidget(self._region_combo, stretch=1)
        outer.addLayout(region_row)

        self._splitter = QSplitter(Qt.Orientation.Vertical)

        spectrum_host = QWidget()
        spectrum_layout = QVBoxLayout(spectrum_host)
        spectrum_layout.setContentsMargins(0, 0, 0, 0)
        self._plot = pg.PlotWidget()
        self._plot.setLabel("bottom", "Wavelength", units="nm")
        self._plot.setLabel("left", "Intensity", units="")
        self._plot.showGrid(x=True, y=True, alpha=0.3)
        self._curve = self._plot.plot()
        spectrum_layout.addWidget(self._plot)
        self._splitter.addWidget(spectrum_host)

        # Slot 1: quicklook panel; starts as an empty placeholder
        self._splitter.addWidget(QWidget())
        self._splitter.setStretchFactor(0, 2)
        self._splitter.setStretchFactor(1, 1)

        outer.addWidget(self._splitter, stretch=1)

        if cube is not None:
            self._apply_cube(cube)

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def load_file(self, path: Path) -> None:
        """Open a SpectroCube .nc file and refresh all panels."""
        cube = open_cube(path)
        self._apply_cube(cube)

    # ------------------------------------------------------------------ #
    # Drag-and-drop                                                        #
    # ------------------------------------------------------------------ #

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            if any(u.toLocalFile().endswith(".nc") for u in event.mimeData().urls()):
                event.acceptProposedAction()
                return
        event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        for url in event.mimeData().urls():
            local = url.toLocalFile()
            if local.endswith(".nc"):
                self.load_file(Path(local))
                event.acceptProposedAction()
                return
        event.ignore()

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _apply_cube(self, cube: SpectroCubeViewModel) -> None:
        self._cube = cube
        filename = Path(cube.path).name if cube.path else "SpectroCube"
        self.setWindowTitle(f"SpectroView — {filename}")

        self._drop_hint.setVisible(False)
        self._meta_label.setVisible(True)
        self._meta_label.setText(self._metadata_text())

        self._frame_slider.blockSignals(True)
        self._frame_slider.setMaximum(max(0, cube.frame_count - 1))
        self._frame_slider.setValue(0)
        self._frame_slider.setEnabled(True)
        self._frame_slider.blockSignals(False)
        self._frame_label.setText("0")

        self._region_combo.blockSignals(True)
        self._region_combo.clear()
        self._region_combo.addItem("Full spectrum", None)
        for region in available_regions(*cube.wavelength_range):
            self._region_combo.addItem(region.name, region)
        self._region_combo.setEnabled(True)
        self._region_combo.blockSignals(False)

        units = cube.attrs.get("intensity_units", "")
        self._plot.setLabel("left", "Intensity", units=units)

        new_quicklook = QuicklookMapsPanel(cube)
        new_quicklook.frame_clicked.connect(self._on_map_frame_clicked)
        old = self._splitter.replaceWidget(1, new_quicklook)
        if old is not None:
            old.deleteLater()
        self._splitter.setStretchFactor(1, 1)
        self._quicklook = new_quicklook

        self._update_frame_display(0)

    def _metadata_text(self) -> str:
        cube = self._cube
        assert cube is not None
        wmin, wmax = cube.wavelength_range
        attrs = cube.attrs
        lines = [
            f"File: {cube.path}",
            f"Frames: {cube.frame_count}  |  "
            f"Wavelength points: {len(cube.wavelength)}  |  "
            f"Range: {wmin:.2f}–{wmax:.2f} nm",
        ]
        for key in ("instrument_id", "calibration_type", "intensity_units", "shot_number"):
            if key in attrs:
                lines.append(f"{key}: {attrs[key]}")
        return "\n".join(lines)

    def _current_frame(self) -> int:
        return self._frame_slider.value()

    def _selected_region(self) -> WavelengthRegion | None:
        return self._region_combo.currentData()

    def _on_frame_changed(self, frame: int) -> None:
        self._update_frame_display(frame)

    def _on_map_frame_clicked(self, frame: int) -> None:
        self._frame_slider.blockSignals(True)
        self._frame_slider.setValue(frame)
        self._frame_slider.blockSignals(False)
        self._update_frame_display(frame)

    def _on_region_changed(self, _index: int) -> None:
        self._update_spectrum()

    def _update_frame_display(self, frame: int) -> None:
        self._frame_label.setText(str(frame))
        self._update_spectrum()
        if self._quicklook is not None:
            self._quicklook.set_frame(frame)

    def _update_spectrum(self) -> None:
        if self._cube is None:
            return
        frame = self._current_frame()
        region = self._selected_region()
        if region is None:
            wl, y = self._cube.spectrum(frame)
            self._plot.setXRange(wl[0], wl[-1], padding=0)
        else:
            wl, y = self._cube.region(frame, region.lo_nm, region.hi_nm)
            self._plot.setXRange(region.lo_nm, region.hi_nm, padding=0)
        self._curve.setData(wl, y)
