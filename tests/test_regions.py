from spectroview.regions import BUILTIN_REGIONS, available_regions


def test_available_regions_filters_by_overlap():
    # Cube covers visible Balmer lines but not full Fulcher upper bound overlap edge cases
    regions = available_regions(430.0, 660.0)
    names = [r.name for r in regions]
    assert "H-alpha" in names
    assert "H-beta" in names
    assert "BH Q-branch" in names
    assert "Fulcher" in names


def test_available_regions_empty_when_no_overlap():
    regions = available_regions(900.0, 1000.0)
    assert regions == []


def test_all_builtin_regions_have_valid_bounds():
    for region in BUILTIN_REGIONS:
        assert region.lo_nm < region.hi_nm
