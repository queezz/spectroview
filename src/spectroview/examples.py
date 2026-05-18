"""Bundled example data for spectroview.

The single demo cube ships inside the package so users can try spectroview
immediately after install without supplying their own file.
"""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path


def get_example_cube_path() -> Path:
    """Return a filesystem path to the bundled 193777 demo SpectroCube.

    Works for editable installs and regular pip installs.  The package is
    never distributed as a zip archive (it contains a GUI), so a direct
    ``Path`` conversion is safe.
    """
    return Path(files("spectroview.data").joinpath("193777_demo.nc"))
