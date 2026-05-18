import numpy as np
import pytest
import xarray as xr

from spectroview.model import NonMonotonicWavelengthError, SpectroCubeViewModel
from tests.conftest import make_synthetic_dataset


def test_view_model_from_synthetic_dataset():
    ds = make_synthetic_dataset()
    cube = SpectroCubeViewModel(ds, path="/tmp/test.nc")
    assert cube.frame_count == 4
    assert cube.wavelength_range == (400.0, 500.0)
    wl, y = cube.spectrum(1)
    assert wl.shape == (50,)
    assert y.shape == (50,)
    assert y[0] == 50.0


def test_region_slices_wavelength():
    ds = make_synthetic_dataset()
    cube = SpectroCubeViewModel(ds)
    wl, y = cube.region(0, 410.0, 420.0)
    assert wl.min() >= 410.0
    assert wl.max() <= 420.0
    assert len(wl) == len(y)


def test_non_monotonic_wavelength_raises():
    wl = np.array([400.0, 410.0, 405.0, 420.0])
    ds = make_synthetic_dataset(n_frames=2, n_wl=4, wavelength=wl)
    with pytest.raises(NonMonotonicWavelengthError):
        SpectroCubeViewModel(ds)


def test_wrong_intensity_dims_raises():
    ds = xr.Dataset(
        {"intensity": (["wavelength"], np.ones(10))},
        coords={"wavelength": np.linspace(400, 500, 10)},
    )
    with pytest.raises(ValueError, match="frame"):
        SpectroCubeViewModel(ds)
