from importlib.resources import files


def test_application_icon_asset_is_packaged() -> None:
    icon = files("spectroview").joinpath("assets/spectrocube_icon.svg")

    assert icon.is_file()
    assert icon.read_text(encoding="utf-8").lstrip().startswith("<svg")
