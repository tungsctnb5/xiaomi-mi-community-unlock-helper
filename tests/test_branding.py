from pathlib import Path

def test_product_branding():
    root=Path(__file__).parents[1]
    main=(root/"app/main.py").read_text(encoding="utf-8")
    spec=(root/"XiaomiUnlockHelper.spec").read_text(encoding="utf-8")
    assert "Xiaomi Mi Community Unlock Helper" in main
    assert "Xiaomi Mi Community Unlock Helper.app" in spec
