from unittest.mock import patch, MagicMock

import requests
from flask import Flask
from flask_turnstile import Turnstile


def _mock_response(status_code=200, success=True):
    """Build a fake requests.Response for the Cloudflare siteverify endpoint."""
    return MagicMock(status_code=status_code, **{"json.return_value": {"success": success}})


app = Flask(__name__)
app.config.update({
    "debug": True,
    "TURNSTILE_SITE_KEY": "SITE_KEY",
    "TURNSTILE_SECRET_KEY": "SECRET",
    "TURNSTILE_ENABLED": True
})

def test_turnstile_enabled():
    turnstile = Turnstile(site_key="SITE_KEY", secret_key="SECRET_KEY")
    assert isinstance(turnstile, Turnstile)
    assert turnstile.is_enabled == True
    assert "script" in turnstile.get_code()
    with patch("flask_turnstile.requests.post", return_value=_mock_response(success=False)):
        assert turnstile.verify(response="None", remote_ip="0.0.0.0") == False

def test_turnstile_enabled_flask():
    turnstile = Turnstile(app=app)
    assert isinstance(turnstile, Turnstile)
    assert turnstile.is_enabled == True
    assert "script" in turnstile.get_code()
    with patch("flask_turnstile.requests.post", return_value=_mock_response(success=False)):
        assert turnstile.verify(response="None", remote_ip="0.0.0.0") == False

def test_verify_success():
    turnstile = Turnstile(site_key="SITE_KEY", secret_key="SECRET_KEY")
    with patch("flask_turnstile.requests.post", return_value=_mock_response(success=True)) as post:
        assert turnstile.verify(response="good", remote_ip="1.2.3.4") == True
        # the configured timeout must reach requests.post so a worker can't hang
        assert post.call_args.kwargs.get("timeout") == Turnstile.DEFAULT_TIMEOUT

def test_verify_failure():
    turnstile = Turnstile(site_key="SITE_KEY", secret_key="SECRET_KEY")
    with patch("flask_turnstile.requests.post", return_value=_mock_response(success=False)):
        assert turnstile.verify(response="bad", remote_ip="1.2.3.4") == False

def test_verify_network_error():
    turnstile = Turnstile(site_key="SITE_KEY", secret_key="SECRET_KEY")
    with patch("flask_turnstile.requests.post", side_effect=requests.ConnectionError):
        assert turnstile.verify(response="x", remote_ip="1.2.3.4") == False

def test_verify_non_200():
    turnstile = Turnstile(site_key="SITE_KEY", secret_key="SECRET_KEY")
    with patch("flask_turnstile.requests.post", return_value=_mock_response(status_code=500)):
        assert turnstile.verify(response="x", remote_ip="1.2.3.4") == False

def test_verify_custom_timeout():
    turnstile = Turnstile(site_key="SITE_KEY", secret_key="SECRET_KEY")
    with patch("flask_turnstile.requests.post", return_value=_mock_response(success=True)) as post:
        turnstile.verify(response="x", remote_ip="1.2.3.4", timeout=3)
        assert post.call_args.kwargs.get("timeout") == 3

def test_turnstile_theme_default():
    turnstile = Turnstile(site_key="SITE_KEY", secret_key="SECRET_KEY")
    assert "data-theme" not in turnstile.get_code()

def test_turnstile_theme_set():
    turnstile = Turnstile(site_key="SITE_KEY", secret_key="SECRET_KEY", theme="dark")
    assert 'data-theme="dark"' in turnstile.get_code()

def test_turnstile_theme_flask():
    app.config.update({
        "TURNSTILE_ENABLED": True,
        "TURNSTILE_THEME": "light"
    })
    turnstile = Turnstile(app=app)
    assert 'data-theme="light"' in turnstile.get_code()

def test_turnstile_size():
    turnstile = Turnstile(site_key="SITE_KEY", secret_key="SECRET_KEY", size="compact")
    assert 'data-size="compact"' in turnstile.get_code()

def test_turnstile_multiple_options():
    turnstile = Turnstile(site_key="SITE_KEY", secret_key="SECRET_KEY",
                          theme="dark", size="flexible", language="es")
    code = turnstile.get_code()
    assert 'data-theme="dark"' in code
    assert 'data-size="flexible"' in code
    assert 'data-language="es"' in code

def test_turnstile_bool_option():
    turnstile = Turnstile(site_key="SITE_KEY", secret_key="SECRET_KEY", response_field=False)
    assert 'data-response-field="false"' in turnstile.get_code()

def test_turnstile_options_via_flask_config():
    app.config.update({
        "TURNSTILE_ENABLED": True,
        "TURNSTILE_THEME": "auto",
        "TURNSTILE_SIZE": "normal"
    })
    turnstile = Turnstile(app=app)
    code = turnstile.get_code()
    assert 'data-theme="auto"' in code
    assert 'data-size="normal"' in code

def test_turnstile_unknown_kwarg_ignored():
    turnstile = Turnstile(site_key="SITE_KEY", secret_key="SECRET_KEY", bogus="x")
    assert "bogus" not in turnstile.get_code()

def test_turnstile_disabled():
    turnstile = Turnstile(site_key="SITE_KEY", secret_key="SECRET_KEY", is_enabled=False)
    assert turnstile.is_enabled == False
    assert turnstile.get_code() == ""
    assert turnstile.verify(response="None", remote_ip="0.0.0.0") == True

def test_turnstile_disabled_flask():
    app.config.update({
        "TURNSTILE_ENABLED": False
    })
    turnstile = Turnstile(app=app)
    assert turnstile.is_enabled == False
    assert turnstile.get_code() == ""
    assert turnstile.verify(response="None", remote_ip="0.0.0.0") == True
