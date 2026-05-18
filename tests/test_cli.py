from spectroview.cli import main


def test_cli_info(capsys, tmp_path):
    path = tmp_path / "tiny.nc"
    from tests.conftest import make_synthetic_dataset

    make_synthetic_dataset().to_netcdf(path)
    code = main(["--info", str(path)])
    assert code == 0
    out = capsys.readouterr().out
    assert "file:" in out
    assert "frame count: 4" in out
