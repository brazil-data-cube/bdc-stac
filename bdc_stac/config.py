#
# This file is part of bdc-stac.
# Copyright (C) 2019 INPE.
#
# bdc-stac is a free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Config module."""

import os

BDC_STAC_BASE_URL = os.getenv('BDC_STAC_BASE_URL', 'http://localhost:5000')
BDC_STAC_API_VERSION = os.getenv('BDC_STAC_API_VERSION', '0.8.1')
BDC_STAC_FILE_ROOT = os.getenv('BDC_STAC_FILE_ROOT', 'http://localhost:5001')
BDC_STAC_MAX_LIMIT = os.getenv('BDC_STAC_MAX_LIMIT', '1000')

BDC_AUTH_CLIENT_SECRET = os.getenv('BDC_AUTH_CLIENT_SECRET', None)
BDC_AUTH_CLIENT_ID = os.getenv('BDC_AUTH_CLIENT_ID', None)
BDC_AUTH_ACCESS_TOKEN_URL = os.getenv('BDC_AUTH_ACCESS_TOKEN_URL', None)

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 
                                    'postgresql://{}:{}@{}:{}/{}'.format(os.getenv('DB_USER'),
                                                                        os.getenv('DB_PASS'),
                                                                        os.getenv('DB_HOST'),
                                                                        os.getenv('DB_PORT'),
                                                                        os.getenv('DB_NAME')))
