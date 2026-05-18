import numpy as np
import xarray as xr


def make_synthetic_dataset(
    n_frames: int = 4,
    n_wl: int = 50,
    *,
    wavelength: np.ndarray | None = None,
) -> xr.Dataset:
    if wavelength is None:
        wavelength = np.linspace(400.0, 500.0, n_wl)
    intensity = np.arange(n_frames * n_wl, dtype=float).reshape(n_frames, n_wl)
    return xr.Dataset(
        {"intensity": (["frame", "wavelength"], intensity)},
        coords={
            "frame": np.arange(n_frames, dtype=float),
            "wavelength": wavelength,
        },
        attrs={
            "spectrocube_version": "0.1.0",
            "instrument_id": "test",
            "calibration_type": "counts",
            "intensity_units": "counts",
            "wavelength_medium": "air",
        },
    )
