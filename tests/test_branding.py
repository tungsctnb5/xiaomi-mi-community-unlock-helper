from pathlib import Path

def test_product_branding():
    root=Path(__file__).parents[1]
    main=(root/"app/main.py").read_text(encoding="utf-8")
    spec=(root/"XiaomiUnlockHelper.spec").read_text(encoding="utf-8")
    assert "Xiaomi Mi Community Unlock Helper" in main
    assert "Xiaomi Mi Community Unlock Helper.app" in spec

def test_attempt_fields_have_readable_minimum_width():
    root=Path(__file__).parents[1]
    source=(root/"app/gui/main_window.py").read_text(encoding="utf-8")
    assert "spin.setMinimumWidth(150)" in source
    assert "QSizePolicy.Expanding" in source
