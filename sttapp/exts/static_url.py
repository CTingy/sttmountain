from functools import partial
from urllib.parse import urljoin
from flask import url_for


def init_static(app):

    static_loc = app.config.get("STATIC_STORAGE_URL")
    static_url = partial(_static_url, static_loc=static_loc)
    app.add_template_global(static_url, 'static_url')


def _static_url(filename, static_loc):

    if static_loc:
        return urljoin(static_loc, filename)
    return url_for('static', filename=filename)
