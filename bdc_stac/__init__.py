#
# This file is part of bdc-stac.
# Copyright (C) 2019 INPE.
#
# bdc-stac is a free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Spatio Temporal Asset Catalog implementation for BDC."""
import logging

from flask import Flask
from flask_redoc import Redoc

from . import config as _config
from .controller import db
from .version import __version__

__all__ = ("__version__",)


def create_app():
    """Flask create app function."""
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = _config.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = _config.SQLALCHEMY_TRACK_MODIFICATIONS

    app.config["BDC_AUTH_CLIENT_SECRET"] = _config.BDC_AUTH_CLIENT_SECRET
    app.config["BDC_AUTH_CLIENT_ID"] = _config.BDC_AUTH_CLIENT_ID
    app.config["BDC_AUTH_ACCESS_TOKEN_URL"] = _config.BDC_AUTH_ACCESS_TOKEN_URL

    app.config["JSONIFY_PRETTYPRINT_REGULAR"] = False
    app.config["JSON_SORT_KEYS"] = False
    app.config["REDOC"] = {"title": "BDC-STAC"}

    if __debug__:
        app.logger.setLevel(logging.DEBUG)

    with app.app_context():
        db.init_app(app)
        Redoc(app, 'spec/openapi.yaml')

        from . import views

    return app
