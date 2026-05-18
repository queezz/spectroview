import numpy as np

from spectroview.gui.quicklook_maps import (
    build_balmer_composite,
    extract_region_cube,
)


def _synthetic_intensity(n_frames: int = 5, n_wl: int = 800) -> tuple[np.ndarray, np.ndarray]:
    wavelength = np.linspace(400.0, 700.0, n_wl)
    intensity = np.random.default_rng(0).random((n_frames, n_wl))
    return intensity, wavelength


def test_extract_region_cube_shape():
    intensity, wavelength = _synthetic_intensity()
    band, wl = extract_region_cube(intensity, wavelength, 655.0, 657.5)
    assert band.shape[0] == 5
    assert band.shape[1] == wl.size
    assert wl.min() >= 655.0
    assert wl.max() <= 657.5


def test_balmer_composite_has_four_bands_and_separators():
    intensity, wavelength = _synthetic_intensity()
    composite, bands = build_balmer_composite(intensity, wavelength)
    assert composite.shape[0] == intensity.shape[0]
    assert len(bands) == 4
    labels = [b.label for b in bands]
    assert labels == ["Hδ", "Hγ", "Hβ", "Hα"]
    # separator columns between bands → wider than sum of individual bands alone
    total_band_cols = sum(b.col_end - b.col_start for b in bands)
    assert composite.shape[1] > total_band_cols
