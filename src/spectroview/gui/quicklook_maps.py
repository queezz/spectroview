"""Hardcoded spectroscopy quicklook maps (Balmer, BH, Fulcher)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from spectroview.model import SpectroCubeViewModel

# Balmer composite bands: label, lo_nm, hi_nm
_BALMER_BANDS: tuple[tuple[str, float, float], ...] = (
    ("Hδ", 409.5, 411.5),
    ("Hγ", 433.0, 435.0),
    ("Hβ", 485.0, 487.0),
    ("Hα", 655.0, 657.5),
)

_BH_BAND = (432.5, 434.5)
_FULCHER_BAND = (590.0, 650.0)

_SEPARATOR_COLS = 3


@dataclass(frozen=True)
class BandSlice:
    """Column range and label within a composite map image."""

    col_start: int
    col_end: int
    label: str


def extract_region_cube(
    intensity: np.ndarray,
    wavelength: np.ndarray,
    lo_nm: float,
    hi_nm: float,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Extract intensity sub-cube for one wavelength window.

    Returns (n_frames, n_wavelength_in_region) and the wavelength axis slice.
    """
    mask = (wavelength >= lo_nm) & (wavelength <= hi_nm)
    if not np.any(mask):
        return np.empty((intensity.shape[0], 0)), wavelength[mask]
    return intensity[:, mask], wavelength[mask]


def build_balmer_composite(
    intensity: np.ndarray,
    wavelength: np.ndarray,
) -> tuple[np.ndarray, list[BandSlice]]:
    """
    Build horizontal composite | Hδ | Hγ | Hβ | Hα | with blank separator columns.
    """
    parts: list[np.ndarray] = []
    bands: list[BandSlice] = []
    col = 0
    n_frames = intensity.shape[0]
    separator = np.full((n_frames, _SEPARATOR_COLS), np.nan)

    for label, lo_nm, hi_nm in _BALMER_BANDS:
        band, _ = extract_region_cube(intensity, wavelength, lo_nm, hi_nm)
        if band.size == 0:
            continue
        if parts:
            parts.append(separator)
            col += _SEPARATOR_COLS
        col_start = col
        parts.append(band)
        col += band.shape[1]
        bands.append(BandSlice(col_start, col, label))

    if not parts:
        empty = np.empty((n_frames, 0))
        return empty, bands
    return np.hstack(parts), bands


def _display_image(image: np.ndarray) -> np.ndarray:
    """Replace NaN separator columns with a value below the data range for display."""
    out = image.astype(float, copy=True)
    finite = np.isfinite(out)
    if not np.any(finite):
        return out
    fill = float(np.nanmin(out[finite])) - 1.0
    out[~finite] = fill
    return out


class QuicklookMapWidget(QWidget):
    """Single frame×wavelength quicklook map with frame cursor and click-to-seek."""

    frame_clicked = Signal(int)

    def __init__(
        self,
        title: str,
        image: np.ndarray,
        *,
        band_slices: list[BandSlice] | None = None,
    ) -> None:
        super().__init__()
        self._image = image  # (n_frames, n_width)
        self._n_frames = image.shape[0]
        self._band_slices = band_slices or []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QLabel(title))

        self._plot = pg.PlotWidget()
        self._plot.setMenuEnabled(False)
        self._plot.setMouseEnabled(x=False, y=True)
        self._plot.hideAxis("bottom")
        self._plot.setLabel("left", "Frame")
        self._plot.invertY(False)
        layout.addWidget(self._plot)

        # pyqtgraph: first array axis = x, second = y → transpose so x=λ, y=frame
        display = _display_image(image)
        self._img_item = pg.ImageItem(display.T, autoLevels=True)
        self._plot.addItem(self._img_item)

        n_width = image.shape[1]
        self._plot.setXRange(-0.5, max(n_width - 0.5, 0.5), padding=0)
        self._plot.setYRange(-0.5, max(self._n_frames - 0.5, 0.5), padding=0)

        self._frame_line = pg.InfiniteLine(
            pos=0,
            angle=0,
            pen=pg.mkPen("y", width=2),
            movable=False,
        )
        self._plot.addItem(self._frame_line)

        for band in self._band_slices:
            if band.col_start > 0:
                self._plot.addItem(
                    pg.InfiniteLine(
                        pos=band.col_start - 0.5,
                        angle=90,
                        pen=pg.mkPen("w", width=1, style=Qt.PenStyle.DashLine),
                    )
                )
            center = 0.5 * (band.col_start + band.col_end - 1)
            text = pg.TextItem(band.label, color="w", anchor=(0.5, 1))
            text.setPos(center, -0.8)
            self._plot.addItem(text)

        self._plot.scene().sigMouseClicked.connect(self._on_mouse_clicked)

    def set_frame(self, frame: int) -> None:
        self._frame_line.setPos(frame)

    def _on_mouse_clicked(self, event) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            return
        pos = self._plot.plotItem.vb.mapSceneToView(event.scenePos())
        frame = int(round(pos.y()))
        frame = max(0, min(frame, self._n_frames - 1))
        self.frame_clicked.emit(frame)


def create_map_widget(
    title: str,
    image: np.ndarray,
    *,
    band_slices: list[BandSlice] | None = None,
) -> QuicklookMapWidget:
    return QuicklookMapWidget(title, image, band_slices=band_slices)


class QuicklookMapsPanel(QWidget):
    """Lower panel: Balmer, BH, and Fulcher quicklook maps."""

    frame_clicked = Signal(int)

    def __init__(self, cube: SpectroCubeViewModel) -> None:
        super().__init__()
        intensity = np.asarray(cube.intensity.values, dtype=float)
        wavelength = cube.wavelength

        balmer_img, balmer_bands = build_balmer_composite(intensity, wavelength)
        bh_img, _ = extract_region_cube(intensity, wavelength, *_BH_BAND)
        fulcher_img, _ = extract_region_cube(intensity, wavelength, *_FULCHER_BAND)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._maps: list[QuicklookMapWidget] = []
        specs: list[tuple[str, np.ndarray, list[BandSlice] | None]] = [
            ("Balmer", balmer_img, balmer_bands),
            ("BH", bh_img, None),
            ("Fulcher", fulcher_img, None),
        ]
        for title, image, bands in specs:
            widget = create_map_widget(title, image, band_slices=bands)
            widget.frame_clicked.connect(self.frame_clicked.emit)
            layout.addWidget(widget, stretch=1)
            self._maps.append(widget)

    def set_frame(self, frame: int) -> None:
        for widget in self._maps:
            widget.set_frame(frame)
