"""SpectroCube viewer — read-only plotting and GUI for calibrated spectral cubes."""

from spectroview.io import open_cube
from spectroview.model import SpectroCubeViewModel

__all__ = ["SpectroCubeViewModel", "open_cube"]
