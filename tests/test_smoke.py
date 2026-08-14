def test_import_gui():
    from app.gui.main_window import MainWindow
    assert MainWindow

def test_login_uses_signed_gateway_flow():
    from app.auth.browser import LOGIN_URL
    assert "/user/login-in?callbackurl=" in LOGIN_URL
    assert "account.xiaomi.com/fe/service/login" not in LOGIN_URL
