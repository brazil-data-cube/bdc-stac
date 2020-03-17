#
# This file is part of bdc-stac.
# Copyright (C) 2019 INPE.
#
# bdc-stac is a free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Spatio Temporal Asset Catalog implementation for BDC."""
import os

from bdc_db import BDCDatabase
from flask import Flask
from flask_redoc import Redoc

from .version import __version__

__all__ = ('__version__',
           'app')


def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{}:{}@{}/{}'.format(os.environ.get('DB_USER'),
                                             os.environ.get('DB_PASS'),
                                             os.environ.get('DB_HOST'),
                                             os.environ.get('DB_NAME'))

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['REDOC'] = {'title': 'BDC-STAC'}

    with app.app_context():
        BDCDatabase(app)
        Redoc(f'spec/api/{os.environ.get("API_VERSION", "0.8.0")}/STAC.yaml', app)

        from . import routes

    return app
