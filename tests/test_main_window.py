from spectroview.gui.main_window import _region_combo_index
from spectroview.regions import WavelengthRegion


def test_region_combo_index_preserves_matching_region_name() -> None:
    regions = [
        WavelengthRegion("H-beta", 485.0, 487.5),
        WavelengthRegion("H-alpha", 655.5, 657.5),
    ]

    assert _region_combo_index(regions, "H-alpha") == 2


def test_region_combo_index_falls_back_to_full_spectrum() -> None:
    regions = [WavelengthRegion("H-beta", 485.0, 487.5)]

    assert _region_combo_index(regions, "Fulcher") == 0
    assert _region_combo_index(regions, None) == 0
