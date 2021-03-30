#
# This file is part of bdc-stac.
# Copyright (C) 2019 INPE.
#
# bdc-stac is a free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Config module."""

import os

from packaging import version as _version

from .version import __version__

SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/bdc")
SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", False)
SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", False)


BDC_STAC_API_VERSION = _version.parse(__version__).base_version
BDC_STAC_BASE_URL = os.getenv("BDC_STAC_BASE_URL", "http://localhost:5000")
BDC_STAC_FILE_ROOT = os.getenv("BDC_STAC_FILE_ROOT", "http://localhost:5001")
BDC_STAC_PNG_ROOT = os.getenv("BDC_STAC_PNG_ROOT", "http://localhost:5001")
BDC_STAC_MAX_LIMIT = int(os.getenv("BDC_STAC_MAX_LIMIT", "1000"))
BDC_STAC_TITLE = os.getenv("BDC_STAC_TITLE", "Brazil Data Cube Catalog")
BDC_STAC_ID = os.getenv("BDC_STAC_ID", "bdc")
BDC_STAC_ASSETS_ARGS = os.getenv("BDC_STAC_ASSETS_ARGS", None)
BDC_AUTH_CLIENT_SECRET = os.getenv("BDC_AUTH_CLIENT_SECRET", None)
BDC_AUTH_CLIENT_ID = os.getenv("BDC_AUTH_CLIENT_ID", None)
BDC_AUTH_ACCESS_TOKEN_URL = os.getenv("BDC_AUTH_ACCESS_TOKEN_URL", None)
