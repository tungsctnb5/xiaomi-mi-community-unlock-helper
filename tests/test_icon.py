from pathlib import Path

def test_icon_assets_and_bundle_config():
    root=Path(__file__).parents[1]
    assert (root/"assets/app-icon-macos.png").stat().st_size>1000
    assert (root/"assets/AppIconRounded.icns").stat().st_size>1000
    assert 'icon="assets/AppIconRounded.icns"' in (root/"XiaomiUnlockHelper.spec").read_text()
