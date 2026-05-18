"""Load SpectroCube netCDF files into a view model."""

from __future__ import annotations

from pathlib import Path

import xarray as xr

from spectroview.model import SpectroCubeViewModel


def open_cube(path: str | Path) -> SpectroCubeViewModel:
    """
    Open a SpectroCube netCDF file read-only and return a view model.

    The file is opened with xarray; no dataset values are modified.
    """
    path = Path(path)
    ds = xr.open_dataset(path)
    return SpectroCubeViewModel(ds, path=str(path.resolve()))
