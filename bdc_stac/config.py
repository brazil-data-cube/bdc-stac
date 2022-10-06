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
"""Config module."""

import os
from distutils.util import strtobool

SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/bdc")
"""The database URI that should be used for the database connection. 
Defaults to ``'postgresql://postgres:postgres@localhost:5432/bdc'``."""

SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", False)
"""Enable (True) or disable (False) signals before and after changes are committed to the database. 
Defaults to ``False``."""

SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", False)
"""Enables or disable debug output of statements to ``stderr``. Defaults to ``False``."""

SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_size": int(os.getenv("SQLALCHEMY_ENGINE_POOL_SIZE", 5)),
    "max_overflow": int(os.getenv("SQLALCHEMY_ENGINE_MAX_OVERFLOW", 10)),
    "poolclass": os.getenv("SQLALCHEMY_ENGINE_POOL_CLASS"),
    "pool_recycle": int(os.getenv("SQLALCHEMY_ENGINE_POOL_RECYCLE", -1)),
}
"""Set SQLAlchemy engine options for pooling.
You may set the following environment variables to customize pooling:

- ``SQLALCHEMY_ENGINE_POOL_SIZE``: The pool size. Defaults to ``5``.
- ``SQLALCHEMY_ENGINE_MAX_OVERFLOW``: Max pool overflow. Defaults to ``10``.
- ``SQLALCHEMY_ENGINE_POOL_CLASS``: The pool type for management. Defaults to ``10``.
- ``SQLALCHEMY_ENGINE_POOL_RECYCLE``: Define the given number of seconds to recycle pool. Defaults to ``-1``, or no timeout.
"""

BDC_STAC_API_VERSION = os.getenv("BDC_STAC_API_VERSION", "1.0.0-rc.1")
BDC_STAC_BASE_URL = os.getenv("BDC_STAC_BASE_URL", "http://localhost:5000")
BDC_STAC_FILE_ROOT = os.getenv("BDC_STAC_FILE_ROOT", "http://localhost:5001")
BDC_STAC_MAX_LIMIT = int(os.getenv("BDC_STAC_MAX_LIMIT", "1000"))
BDC_STAC_TITLE = os.getenv("BDC_STAC_TITLE", "Brazil Data Cube Catalog")
BDC_STAC_ID = os.getenv("BDC_STAC_ID", "bdc")
BDC_STAC_ASSETS_ARGS = os.getenv("BDC_STAC_ASSETS_ARGS", "access_token")
BDC_AUTH_CLIENT_SECRET = os.getenv("BDC_AUTH_CLIENT_SECRET", None)
BDC_AUTH_CLIENT_ID = os.getenv("BDC_AUTH_CLIENT_ID", None)
BDC_AUTH_ACCESS_TOKEN_URL = os.getenv("BDC_AUTH_ACCESS_TOKEN_URL", None)
BDC_STAC_USE_FOOTPRINT = strtobool(os.getenv('BDC_STAC_USE_FOOTPRINT', '0'))
"""Flag to set if Item intersection should use ``Item.footprint``.
Defaults to ``0``, which means to use ``Item.bbox``."""

STAC_GEO_MEDIA_TYPE = "application/geo+json"
