#
# This file is part of BDC-STAC.
# Copyright (C) 2022 INPE.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.
#

"""Spatio Temporal Asset Catalog implementation for BDC."""
import logging

from bdc_catalog import BDCCatalog
from flask import Flask
from flask_redoc import Redoc

from . import config as _config
from .controller import db
from .version import __version__

__all__ = ("__version__", "create_app")


def create_app():
    """Flask create app function."""
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = _config.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = _config.SQLALCHEMY_TRACK_MODIFICATIONS

    app.config["BDC_AUTH_CLIENT_SECRET"] = _config.BDC_AUTH_CLIENT_SECRET
    app.config["BDC_AUTH_CLIENT_ID"] = _config.BDC_AUTH_CLIENT_ID
    app.config["BDC_AUTH_ACCESS_TOKEN_URL"] = _config.BDC_AUTH_ACCESS_TOKEN_URL

    # Disable JSON pretty serialization.
    app.json.compact = True
    app.json.sort_keys = False
    app.config["REDOC"] = {"title": "BDC-STAC"}

    if __debug__:
        app.logger.setLevel(logging.DEBUG)

    with app.app_context():
        BDCCatalog(app)
        db.init_app(app)
        Redoc(app, "spec/openapi.yaml")

        from . import views

    return app
