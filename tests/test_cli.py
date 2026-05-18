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


def test_cli_info_without_file(capsys):
    code = main(["--info"])
    assert code == 1
    err = capsys.readouterr().err
    assert "error" in err


def test_cli_info_file_not_found(capsys):
    code = main(["--info", "/nonexistent/path.nc"])
    assert code == 1
    err = capsys.readouterr().err
    assert "file not found" in err


def test_cli_file_not_found(capsys):
    code = main(["/nonexistent/path.nc"])
    assert code == 1
    err = capsys.readouterr().err
    assert "file not found" in err


def test_cli_no_args_launches_gui_with_demo(monkeypatch):
    import spectroview.gui.app as app_module
    from spectroview.examples import get_example_cube_path

    calls: list = []
    monkeypatch.setattr(app_module, "run_gui", lambda path: calls.append(path) or 0)
    code = main([])
    assert code == 0
    assert len(calls) == 1
    # No explicit path → demo cube is passed automatically
    assert calls[0] == get_example_cube_path()


def test_cli_with_file_launches_gui(monkeypatch, tmp_path):
    import spectroview.gui.app as app_module
    from tests.conftest import make_synthetic_dataset

    path = tmp_path / "tiny.nc"
    make_synthetic_dataset().to_netcdf(path)

    calls: list = []
    monkeypatch.setattr(app_module, "run_gui", lambda p: calls.append(p) or 0)
    code = main([str(path)])
    assert code == 0
    assert len(calls) == 1
    assert calls[0] == path
