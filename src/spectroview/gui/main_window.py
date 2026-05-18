"""Main spectroview window."""

from __future__ import annotations

import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from spectroview.model import SpectroCubeViewModel
from spectroview.regions import WavelengthRegion, available_regions


class MainWindow(QMainWindow):
    def __init__(self, cube: SpectroCubeViewModel) -> None:
        super().__init__()
        self._cube = cube
        self._regions: list[WavelengthRegion | None] = [None]
        self._regions.extend(available_regions(*cube.wavelength_range))

        self.setWindowTitle(f"spectroview — {cube.path or 'SpectroCube'}")

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self._meta_label = QLabel(self._metadata_text())
        self._meta_label.setWordWrap(True)
        self._meta_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self._meta_label)

        slider_row = QHBoxLayout()
        slider_row.addWidget(QLabel("Frame:"))
        self._frame_slider = QSlider(Qt.Orientation.Horizontal)
        self._frame_slider.setMinimum(0)
        self._frame_slider.setMaximum(max(0, cube.frame_count - 1))
        self._frame_slider.setValue(0)
        self._frame_slider.valueChanged.connect(self._on_frame_changed)
        slider_row.addWidget(self._frame_slider, stretch=1)
        self._frame_label = QLabel("0")
        slider_row.addWidget(self._frame_label)
        layout.addLayout(slider_row)

        region_row = QHBoxLayout()
        region_row.addWidget(QLabel("Region:"))
        self._region_combo = QComboBox()
        self._region_combo.addItem("Full spectrum", None)
        for region in self._regions[1:]:
            assert region is not None
            self._region_combo.addItem(region.name, region)
        self._region_combo.currentIndexChanged.connect(self._on_region_changed)
        region_row.addWidget(self._region_combo, stretch=1)
        layout.addLayout(region_row)

        self._plot = pg.PlotWidget()
        self._plot.setLabel("bottom", "Wavelength", units="nm")
        units = cube.attrs.get("intensity_units", "")
        self._plot.setLabel("left", "Intensity", units=units)
        self._plot.showGrid(x=True, y=True, alpha=0.3)
        self._curve = self._plot.plot()
        layout.addWidget(self._plot, stretch=1)

        self._update_spectrum()

    def _metadata_text(self) -> str:
        cube = self._cube
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
        self._frame_label.setText(str(frame))
        self._update_spectrum()

    def _on_region_changed(self, _index: int) -> None:
        self._update_spectrum()

    def _update_spectrum(self) -> None:
        frame = self._current_frame()
        region = self._selected_region()
        if region is None:
            wl, y = self._cube.spectrum(frame)
            self._plot.setXRange(wl[0], wl[-1], padding=0)
        else:
            wl, y = self._cube.region(frame, region.lo_nm, region.hi_nm)
            self._plot.setXRange(region.lo_nm, region.hi_nm, padding=0)
        self._curve.setData(wl, y)
