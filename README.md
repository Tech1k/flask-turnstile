# Flask-Turnstile
[![Latest version released on PyPi](https://img.shields.io/pypi/v/Flask-Turnstile.svg?style=flat&label=latest%20version)](https://pypi.org/project/Flask-Turnstile/)
[![PyPi monthly downloads](https://img.shields.io/pypi/dm/Flask-Turnstile)](https://img.shields.io/pypi/dm/Flask-Turnstile)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

A Cloudflare Turnstile extension for Flask based on flask-recaptcha.

---

## Install
```
pip install flask-turnstile
```

# Usage

### Implementation view.py
```
from flask import Flask
from flask_turnstile import Turnstile

app = Flask(__name__)
turnstile = Turnstile(app=app)

#or 

turnstile = Turnstile()
turnstile.init_app(app)
```

### In your template: **{{ turnstile }}**

Inside of the form you want to protect, include the tag: **{{ turnstile }}**

It will insert the code automatically

```
<form method="post" action="/submit">
    ... your field
    ... your field

    {{ turnstile }}

    [submit button]
</form>
```


### Verify the captcha

In the view that's going to validate the captcha

```
from flask import Flask
from flask_turnstile import Turnstile

app = Flask(__name__)
turnstile = Turnstile(app=app)

@app.route("/submit", methods=["POST"])
def submit():

    if turnstile.verify():
        # SUCCESS
        pass
    else:
        # FAILED
        pass
```


## Api

**turnstile.__init__(app, site_key, secret_key, is_enabled=True)**

**turnstile.get_code()**

Returns the HTML code to implement. But you can use
**{{ turnstile }}** directly in your template

**turnstile.verify()**

Returns bool

## In Template

Just include **{{ turnstile }}** wherever you want to show the captcha


## Config

Flask-Turnstile is configured through the standard Flask config API.
These are the available options:

**TURNSTILE_ENABLED**: Bool - True by default, when False it will bypass validation

**TURNSTILE_SITE_KEY** : Public key

**TURNSTILE_SECRET_KEY**: Private key

The following are **Optional** arguments.

```
TURNSTILE_ENABLED = True
TURNSTILE_SITE_KEY = ""
TURNSTILE_SECRET_KEY = ""
```

### Widget options

Any of the Cloudflare Turnstile [widget options](https://developers.cloudflare.com/turnstile/get-started/client-side-rendering/#configurations) can be set, either through Flask config as `TURNSTILE_<OPTION>` or as a keyword argument to `Turnstile(...)`. Each is rendered as the matching `data-*` attribute on the widget. When an option is left unset it is omitted entirely (so Cloudflare's default applies, e.g. theme follows the visitor's system preference).

| Flask config | Constructor kwarg | Rendered attribute | Common values |
|---|---|---|---|
| `TURNSTILE_THEME` | `theme` | `data-theme` | `auto`, `light`, `dark` |
| `TURNSTILE_SIZE` | `size` | `data-size` | `normal`, `flexible`, `compact` |
| `TURNSTILE_LANGUAGE` | `language` | `data-language` | `auto`, ISO code (e.g. `en`, `es`) |
| `TURNSTILE_APPEARANCE` | `appearance` | `data-appearance` | `always`, `execute`, `interaction-only` |
| `TURNSTILE_ACTION` | `action` | `data-action` | string (max 32 chars) |
| `TURNSTILE_CDATA` | `cdata` | `data-cdata` | string (max 255 chars) |
| `TURNSTILE_TABINDEX` | `tabindex` | `data-tabindex` | integer |
| `TURNSTILE_RETRY` | `retry` | `data-retry` | `auto`, `never` |
| `TURNSTILE_RETRY_INTERVAL` | `retry_interval` | `data-retry-interval` | ms (default `8000`) |
| `TURNSTILE_REFRESH_EXPIRED` | `refresh_expired` | `data-refresh-expired` | `auto`, `manual`, `never` |
| `TURNSTILE_REFRESH_TIMEOUT` | `refresh_timeout` | `data-refresh-timeout` | `auto`, `manual`, `never` |
| `TURNSTILE_EXECUTION` | `execution` | `data-execution` | `render`, `execute` |
| `TURNSTILE_RESPONSE_FIELD` | `response_field` | `data-response-field` | bool |
| `TURNSTILE_RESPONSE_FIELD_NAME` | `response_field_name` | `data-response-field-name` | string |
| `TURNSTILE_FEEDBACK_ENABLED` | `feedback_enabled` | `data-feedback-enabled` | bool |
| `TURNSTILE_CALLBACK` | `callback` | `data-callback` | JS function name |
| `TURNSTILE_ERROR_CALLBACK` | `error_callback` | `data-error-callback` | JS function name |
| `TURNSTILE_EXPIRED_CALLBACK` | `expired_callback` | `data-expired-callback` | JS function name |
| `TURNSTILE_TIMEOUT_CALLBACK` | `timeout_callback` | `data-timeout-callback` | JS function name |
| `TURNSTILE_BEFORE_INTERACTIVE_CALLBACK` | `before_interactive_callback` | `data-before-interactive-callback` | JS function name |
| `TURNSTILE_AFTER_INTERACTIVE_CALLBACK` | `after_interactive_callback` | `data-after-interactive-callback` | JS function name |
| `TURNSTILE_UNSUPPORTED_CALLBACK` | `unsupported_callback` | `data-unsupported-callback` | JS function name |

Example:

```python
TURNSTILE_THEME = "dark"
TURNSTILE_SIZE = "flexible"
```

---

(c) 2015 Mardix
(c) 2023-2026 Kristian
