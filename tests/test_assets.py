from importlib.resources import files
from xml.etree import ElementTree


def test_application_icon_asset_is_packaged() -> None:
    icon = files("spectroview").joinpath("assets/spectrocube_icon.svg")

    assert icon.is_file()
    root = ElementTree.fromstring(icon.read_text(encoding="utf-8"))
    assert root.tag.endswith("svg")
