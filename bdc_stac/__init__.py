import os

from bdc_db import BDCDatabase
from flasgger import Swagger
from flask import Flask

from .version import __version__

__all__ = ('__version__',
           'app')


def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{}:{}@{}/{}'.format(os.environ.get('DB_USER'),
                                             os.environ.get('DB_PASS'),
                                             os.environ.get('DB_HOST'),
                                             os.environ.get('DB_NAME'))

    app.config["SWAGGER"] = {
        "openapi": "3.0.1",
        "specs_route": "/docs",
        "title": "Brazil Data Cube Catalog"
    }

    with app.app_context():
        BDCDatabase(app)
        Swagger(app, template_file="./spec/api/0.7.0/STAC.yaml")

        from . import routes

    return app
