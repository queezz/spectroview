import numpy as np
import pytest

from spectroview.gui.quicklook_maps import (
    _normalize_band,
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


def test_balmer_composite_independent_normalization():
    """Weak lines stay visible even when Hα is 1000x brighter."""
    n_frames = 5
    wavelength = np.linspace(400.0, 700.0, 800)
    intensity = np.zeros((n_frames, len(wavelength)))

    hd_mask = (wavelength >= 409.5) & (wavelength <= 411.5)
    ha_mask = (wavelength >= 655.0) & (wavelength <= 657.5)
    # Both lines vary across frames (needed for normalization to work), but Hα
    # is 1000x brighter.  Without per-band normalization Hδ would appear black.
    frames = np.arange(1, n_frames + 1, dtype=float)[:, np.newaxis]
    intensity[:, hd_mask] = frames * 1.0
    intensity[:, ha_mask] = frames * 1000.0

    composite, bands = build_balmer_composite(intensity, wavelength)
    labels = [b.label for b in bands]
    hd_sl = bands[labels.index("Hδ")]
    ha_sl = bands[labels.index("Hα")]

    hd_cols = composite[:, hd_sl.col_start : hd_sl.col_end]
    ha_cols = composite[:, ha_sl.col_start : ha_sl.col_end]

    # Both bands independently normalized → both should saturate near 1
    assert np.nanmax(hd_cols) > 0.9, "Hδ must be visible after independent normalization"
    assert np.nanmax(ha_cols) > 0.9, "Hα must be visible after independent normalization"


def test_balmer_composite_output_range():
    """Composite pixel values (excluding NaN separators) must lie in [0, 1]."""
    intensity, wavelength = _synthetic_intensity()
    composite, _ = build_balmer_composite(intensity, wavelength)
    finite = composite[np.isfinite(composite)]
    assert finite.min() >= 0.0
    assert finite.max() <= 1.0


# ---------------------------------------------------------------------------
# _normalize_band unit tests
# ---------------------------------------------------------------------------


def test_normalize_band_scales_to_unit_range():
    rng = np.random.default_rng(1)
    band = rng.uniform(0.0, 500.0, (10, 20))
    out = _normalize_band(band)
    assert out.min() >= 0.0
    assert out.max() <= 1.0
    assert out.max() > 0.9  # signal actually reaches top


def test_normalize_band_flat_input_returns_zeros():
    band = np.full((5, 10), 42.0)
    out = _normalize_band(band)
    assert np.all(out == 0.0)


def test_normalize_band_empty_returns_zeros():
    band = np.empty((5, 0))
    out = _normalize_band(band)
    assert out.shape == (5, 0)


def test_normalize_band_all_nan_returns_zeros():
    band = np.full((4, 8), np.nan)
    out = _normalize_band(band)
    assert np.all(out == 0.0)


@pytest.mark.parametrize("amplitude", [1e-12, 1e12])
def test_normalize_band_extreme_amplitudes(amplitude: float):
    rng = np.random.default_rng(2)
    band = rng.uniform(0.0, amplitude, (6, 15))
    out = _normalize_band(band)
    assert out.min() >= 0.0
    assert out.max() <= 1.0
