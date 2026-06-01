"""
A Cloudflare Turnstile extension for Flask based on flask-recaptcha
"""

__NAME__ = "Flask-Turnstile"
__version__ = "0.2.0"
__license__ = "MIT"
__author__ = "Kristian (originally ReCaptcha by Mardix)"
__copyright__ = "(c) 2023-2026 Kristian (originally ReCaptcha by Mardix 2015)"

from typing import Any, Optional

from flask import Flask, request
try:
    from markupsafe import Markup, escape
except ImportError:
    from jinja2 import Markup, escape
import requests

# Deprecated: configuration now lives on each Turnstile instance rather than on
# this shared class. Kept defined for backwards compatibility with any code that
# imported it; it is no longer used internally.
class BlueprintCompatibility(object):
    site_key = None
    secret_key = None
    options = {}

class DEFAULTS(object):
    IS_ENABLED = True


class Turnstile(object):

    VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
    DEFAULT_TIMEOUT = 10
    site_key = None
    secret_key = None
    is_enabled = False

    # Maps a keyword/config name to the Turnstile widget ``data-*`` attribute it
    # renders. Each is settable either as a constructor kwarg (e.g. ``theme=``)
    # or via Flask config as ``TURNSTILE_<NAME>`` (e.g. ``TURNSTILE_THEME``).
    # See https://developers.cloudflare.com/turnstile/get-started/client-side-rendering/
    WIDGET_OPTIONS = {
        "action": "action",
        "cdata": "cdata",
        "callback": "callback",
        "error_callback": "error-callback",
        "expired_callback": "expired-callback",
        "timeout_callback": "timeout-callback",
        "before_interactive_callback": "before-interactive-callback",
        "after_interactive_callback": "after-interactive-callback",
        "unsupported_callback": "unsupported-callback",
        "theme": "theme",
        "language": "language",
        "tabindex": "tabindex",
        "response_field": "response-field",
        "response_field_name": "response-field-name",
        "size": "size",
        "retry": "retry",
        "retry_interval": "retry-interval",
        "refresh_expired": "refresh-expired",
        "refresh_timeout": "refresh-timeout",
        "appearance": "appearance",
        "execution": "execution",
        "feedback_enabled": "feedback-enabled",
    }

    def __init__(self, app: Optional[Flask] = None, site_key: Optional[str] = None,
                 secret_key: Optional[str] = None, is_enabled: bool = True, **kwargs: Any) -> None:
        self.site_key = site_key
        self.secret_key = secret_key
        self.options = {}

        if site_key:
            self.options = {
                self.WIDGET_OPTIONS[name]: value
                for name, value in kwargs.items()
                if name in self.WIDGET_OPTIONS and value is not None
            }
            self.is_enabled = is_enabled

        elif app:
            self.init_app(app=app)

    def init_app(self, app: Optional[Flask] = None) -> None:
        options = {}
        for name in self.WIDGET_OPTIONS:
            value = app.config.get("TURNSTILE_" + name.upper())
            if value is not None:
                options[name] = value

        self.__init__(site_key=app.config.get("TURNSTILE_SITE_KEY"),
                      secret_key=app.config.get("TURNSTILE_SECRET_KEY"),
                      is_enabled=app.config.get("TURNSTILE_ENABLED", DEFAULTS.IS_ENABLED),
                      **options)

        @app.context_processor
        def get_code():
            return dict(turnstile=Markup(self.get_code()))

    @staticmethod
    def _format_value(value: Any) -> str:
        # Render Python booleans the way the Turnstile widget expects them.
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)

    def get_code(self) -> str:
        """
        Returns the new Turnstile captcha code
        :return:
        """
        if not self.is_enabled:
            return ""

        attrs = "".join(
            ' data-{ATTR}="{VALUE}"'.format(ATTR=attr, VALUE=escape(self._format_value(value)))
            for attr, value in self.options.items()
        )

        return ("""
        <script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>
        <div class="cf-turnstile" data-sitekey="{SITE_KEY}"{ATTRS}></div>
        """.format(SITE_KEY=self.site_key, ATTRS=attrs))

    def get_response(self, response: Optional[str] = None, remote_ip: Optional[str] = None,
                     timeout: Optional[float] = None) -> dict:
        """
        Verify the token and return Cloudflare's raw siteverify JSON response.

        Returns a dict that includes "success" and, on failure, "error-codes",
        plus "challenge_ts" and "hostname" when provided by Cloudflare. Returns
        an empty dict when validation is disabled or the request fails.
        :return: dict
        """
        if not self.is_enabled:
            return {}

        data = {
            "secret": self.secret_key,
            "response": response or request.form.get('cf-turnstile-response'),
            "remoteip": remote_ip or request.environ.get('REMOTE_ADDR')
        }

        try:
            r = requests.post(self.VERIFY_URL, data=data,
                              timeout=timeout or self.DEFAULT_TIMEOUT)
        except requests.RequestException:
            return {}
        return r.json() if r.status_code == 200 else {}

    def verify(self, response: Optional[str] = None, remote_ip: Optional[str] = None,
               timeout: Optional[float] = None) -> bool:
        if not self.is_enabled:
            return True
        return self.get_response(response, remote_ip, timeout).get("success", False)
