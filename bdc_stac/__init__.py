#
# This file is part of bdc-stac.
# Copyright (C) 2019 INPE.
#
# bdc-stac is a free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Spatio Temporal Asset Catalog implementation for BDC."""
from bdc_catalog import BDCCatalog
from flask import Flask
from flask_redoc import Redoc

from .version import __version__
from . import config as _config

__all__ = ('__version__')


def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = _config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = _config.SQLALCHEMY_TRACK_MODIFICATIONS

    app.config['BDC_AUTH_CLIENT_SECRET'] = _config.BDC_AUTH_CLIENT_SECRET
    app.config['BDC_AUTH_CLIENT_ID'] = _config.BDC_AUTH_CLIENT_ID
    app.config['BDC_AUTH_ACCESS_TOKEN_URL'] = _config.BDC_AUTH_ACCESS_TOKEN_URL

    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
    app.config['JSON_SORT_KEYS'] = False
    app.config['REDOC'] = {'title': 'BDC-STAC'}

    with app.app_context():
        BDCCatalog(app)
        Redoc(app, f'spec/api/{_config.BDC_STAC_API_VERSION}/STAC.yaml')

        from . import routes

    return app
