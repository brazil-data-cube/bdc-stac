import os

BDC_STAC_BASE_URL = os.getenv('BDC_STAC_BASE_URL', 'http://localhost:5005')
BDC_STAC_API_VERSION = os.getenv('BDC_STAC_API_VERSION', '0.8.1')
BDC_STAC_FILE_ROOT = os.getenv('BDC_STAC_FILE_ROOT', 'http://localhost:5001')

SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}:{}/{}'.format(os.getenv('DB_USER'),
                                                               os.getenv('DB_PASS'),
                                                               os.getenv('DB_HOST'),
                                                               os.getenv('DB_PORT'),
                                                               os.getenv('DB_NAME'))