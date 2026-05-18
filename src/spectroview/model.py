"""Read-only view model over a SpectroCube xarray Dataset."""

from __future__ import annotations

from typing import Any

import numpy as np
import xarray as xr


class NonMonotonicWavelengthError(ValueError):
    """Raised when the wavelength axis is not strictly increasing."""


def _validate_monotonic_wavelength(wavelength: np.ndarray) -> None:
    if wavelength.size < 2:
        return
    if not np.all(np.diff(wavelength) > 0):
        raise NonMonotonicWavelengthError(
            "Wavelength coordinate must be strictly monotonically increasing."
        )


class SpectroCubeViewModel:
    """Thin wrapper around an xarray Dataset with frame × wavelength spectra."""

    def __init__(self, ds: xr.Dataset, *, path: str | None = None) -> None:
        if "intensity" not in ds.data_vars:
            raise ValueError("Dataset has no 'intensity' data variable.")
        if "wavelength" not in ds.coords:
            raise ValueError("Dataset has no 'wavelength' coordinate.")

        intensity_dims = tuple(ds["intensity"].dims)
        if intensity_dims != ("frame", "wavelength"):
            raise ValueError(
                f"Expected intensity dims ('frame', 'wavelength'), got {intensity_dims!r}."
            )

        self._ds = ds
        self._path = path
        self._wavelength = np.asarray(ds["wavelength"].values, dtype=float)
        _validate_monotonic_wavelength(self._wavelength)

    @property
    def path(self) -> str | None:
        return self._path

    @property
    def ds(self) -> xr.Dataset:
        """Underlying xarray Dataset (read-only use)."""
        return self._ds

    @property
    def wavelength(self) -> np.ndarray:
        return self._wavelength

    @property
    def intensity(self) -> xr.DataArray:
        return self._ds["intensity"]

    @property
    def frame_count(self) -> int:
        return int(self._ds.sizes["frame"])

    @property
    def wavelength_range(self) -> tuple[float, float]:
        return float(self._wavelength[0]), float(self._wavelength[-1])

    @property
    def attrs(self) -> dict[str, Any]:
        return dict(self._ds.attrs)

    def spectrum(self, frame: int) -> tuple[np.ndarray, np.ndarray]:
        """Return (wavelength_nm, intensity) for one frame."""
        if frame < 0 or frame >= self.frame_count:
            raise IndexError(f"frame {frame} out of range [0, {self.frame_count})")
        y = np.asarray(self._ds["intensity"].isel(frame=frame).values, dtype=float)
        return self._wavelength.copy(), y

    def region(
        self, frame: int, lo_nm: float, hi_nm: float
    ) -> tuple[np.ndarray, np.ndarray]:
        """Return (wavelength_nm, intensity) clipped to [lo_nm, hi_nm]."""
        wl, y = self.spectrum(frame)
        mask = (wl >= lo_nm) & (wl <= hi_nm)
        return wl[mask], y[mask]
