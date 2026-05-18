from spectroview.io import open_cube
from tests.conftest import make_synthetic_dataset


def test_open_cube_synthetic(tmp_path):
    path = tmp_path / "tiny.nc"
    make_synthetic_dataset().to_netcdf(path)
    cube = open_cube(path)
    assert cube.frame_count == 4
    assert cube.path == str(path.resolve())
