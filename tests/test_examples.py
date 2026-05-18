"""Tests for the bundled demo dataset."""

from pathlib import Path

from spectroview.examples import get_example_cube_path
from spectroview.io import open_cube


def test_example_cube_path_exists():
    path = get_example_cube_path()
    assert isinstance(path, Path)
    assert path.exists(), f"Demo cube not found at {path}"
    assert path.suffix == ".nc"


def test_example_cube_opens():
    cube = open_cube(get_example_cube_path())
    assert cube.frame_count > 0
    wmin, wmax = cube.wavelength_range
    assert wmin < wmax


def test_example_cube_covers_key_regions():
    """All Balmer and molecular band windows must fall within demo wavelength range."""
    cube = open_cube(get_example_cube_path())
    wmin, wmax = cube.wavelength_range

    required_windows = {
        "Hδ": (409.5, 411.5),
        "Hγ / BH": (432.5, 435.0),
        "Hβ": (485.0, 487.0),
        "Fulcher": (590.0, 650.0),
        "Hα": (655.0, 657.5),
    }
    for name, (lo, hi) in required_windows.items():
        assert wmin <= lo and hi <= wmax, (
            f"Demo cube does not cover {name} ({lo}–{hi} nm); "
            f"cube range is {wmin:.1f}–{wmax:.1f} nm"
        )
