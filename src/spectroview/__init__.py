"""SpectroCube viewer — read-only plotting and GUI for calibrated spectral cubes."""

from spectroview.examples import get_example_cube_path
from spectroview.io import open_cube
from spectroview.model import SpectroCubeViewModel

__all__ = ["SpectroCubeViewModel", "get_example_cube_path", "open_cube"]
