"""Matplotlib helpers for notebooks and static plots."""

from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np

from spectroview.regions import BUILTIN_REGIONS

if TYPE_CHECKING:
    from spectroview.model import SpectroCubeViewModel


def _region_by_name(name: str):
    for region in BUILTIN_REGIONS:
        if region.name == name:
            return region
    raise KeyError(f"Unknown region {name!r}. Choose from: {[r.name for r in BUILTIN_REGIONS]}")


def plot_spectrum(cube: SpectroCubeViewModel, frame: int = 0) -> plt.Axes:
    """Plot a single-frame spectrum."""
    wl, y = cube.spectrum(frame)
    fig, ax = plt.subplots()
    ax.plot(wl, y)
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel(cube.attrs.get("intensity_units", "intensity"))
    ax.set_title(f"Frame {frame}")
    fig.tight_layout()
    return ax


def plot_region(cube: SpectroCubeViewModel, region_name: str, frame: int = 0) -> plt.Axes:
    """Plot a named wavelength region."""
    region = _region_by_name(region_name)
    wl, y = cube.region(frame, region.lo_nm, region.hi_nm)
    fig, ax = plt.subplots()
    ax.plot(wl, y)
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel(cube.attrs.get("intensity_units", "intensity"))
    ax.set_title(f"{region.name} — frame {frame}")
    fig.tight_layout()
    return ax


def plot_map(cube: SpectroCubeViewModel) -> plt.Axes:
    """Plot intensity as frame × wavelength image."""
    data = np.asarray(cube.intensity.values, dtype=float)
    fig, ax = plt.subplots()
    wl0, wl1 = cube.wavelength_range
    ax.imshow(
        data,
        aspect="auto",
        origin="lower",
        extent=(wl0, wl1, 0, cube.frame_count),
    )
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Frame")
    ax.set_title("Intensity map")
    fig.tight_layout()
    return ax
