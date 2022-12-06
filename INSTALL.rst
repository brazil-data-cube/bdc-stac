..
    This file is part of BDC-STAC.
    Copyright (C) 2022 INPE.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.


Installation
============


Development Installation
------------------------


Pre-Requirements
++++++++++++++++


The Brazil Data Cube STAC implementation depends essentially on:

- `Flask <https://palletsprojects.com/p/flask/>`_: a lightweight WSGI web application framework.

- `Flask-SQLAlchemy <https://flask-sqlalchemy.palletsprojects.com/en/2.x/>`_: an extension for Flask that adds support of `SQLAlchemy <https://www.sqlalchemy.org/>`_.

- `BDC-Catalog <https://bdc-catalog.readthedocs.io/en/latest/>`_ (v1.0+): an image metadata storage module for Earth Observation imagery of Brazil Data Cube.

- `Flask-Redoc <https://pypi.org/project/flask-redoc/>`_: a Flask extension for displaying OpenAPI/Swagger documentation using Redocs.

All these libraries can be easily installed in the next steps.


STAC Versions
+++++++++++++

Before installing the ``BDC-STAC`` server, please, take a look into compatibility table:

+---------------------------+-----------+-------------+
| STAC API Spec             | BDC-STAC  | BDC-Catalog |
+===========================+===========+=============+
| 0.8.x                     | 0.8.x     | 0.4.x       |
+---------------------------+-----------+-------------+
| 0.9.0        - 1.0.0-rc.1 | 0.9.x     | 0.8.x       |
+---------------------------+-----------+-------------+
| 1.0.0-beta.1 - 1.0.0-rc.1 | 1.0.0     | 1.0.0       |
+---------------------------+-----------+-------------+
| 1.0.0-beta.1 - 1.0.0-rc.1 | 1.0.1     | 1.0.1       |
+---------------------------+-----------+-------------+


Clone the software repository
+++++++++++++++++++++++++++++

Use ``git`` to clone the software repository::

    git clone https://github.com/brazil-data-cube/bdc-stac.git


Install BDC-STAC in Development Mode
++++++++++++++++++++++++++++++++++++

Go to the source code folder::

        $ cd bdc-stac


Install in development mode::

        $ pip3 install -U pip setuptools wheel
        $ pip3 install -e .[all]


.. note::

    If you want to create a new *Python Virtual Environment*, please, follow this instruction:

    *1.* Create a new virtual environment linked to Python 3.7::

        python3.7 -m venv venv


    **2.** Activate the new environment::

        source venv/bin/activate


    **3.** Update pip and setuptools::

        pip3 install --upgrade pip setuptools wheel


Build the Documentation
+++++++++++++++++++++++


You can generate the documentation based on Sphinx with the following command::

    python setup.py build_sphinx


The above command will generate the documentation in HTML and it will place it under::

    docs/sphinx/_build/html/


You can open the above documentation in your favorite browser, as::

    firefox docs/sphinx/_build/html/index.html


Running in Development Mode
+++++++++++++++++++++++++++

.. note::

        Make sure you have a database prepared using `Brazil Data Cube Catalog Module <https://github.com/brazil-data-cube/bdc-catalog>`_.
        You can achieve a minimal database with ``Docker`` using the following steps::

            docker run --name bdc_pg \
                       --detach \
                       --volume bdc_catalog_vol:/var/lib/postgresql/data \
                       --env POSTGRES_PASSWORD=postgres \
                       --publish 5432:5432 \
                       postgis/postgis:12-3.0

        Once container is up and running, initialize the database::

            export SQLALCHEMY_DATABASE_URI="postgresql://postgres:postgres@localhost:5432/bdcdb"
            bdc-db db init
            bdc-db db create-namespaces
            bdc-db db create-extension-postgis
            bdc-db db create-schema # For devmode
            # bdc-db alembic upgrade  # For prod (recommended)

        After that, you can download a minimal collection `sentinel-2.json <https://raw.githubusercontent.com/brazil-data-cube/bdc-catalog/master/examples/fixtures/sentinel-2.json>`_
        JSON example and then load it with ``BDC-Catalog`` command line::

            export SQLALCHEMY_DATABASE_URI="postgresql://postgres:postgres@localhost:5432/bdcdb"
            bdc-catalog load-data --ifile /path/to/sentinel-2.json


In the source code folder, enter the following command:

.. code-block:: shell

        $ FLASK_APP="bdc_stac" \
          SQLALCHEMY_DATABASE_URI="postgresql://postgres:postgres@localhost:5432/bdcdb" \
          BDC_STAC_BASE_URL="http://localhost:5000" \
          BDC_STAC_FILE_ROOT="http://localhost:5001" \
          flask run


You may need to replace the definition of some environment variables:

    - ``SQLALCHEMY_DATABASE_URI="postgresql://postgres:postgres@localhost:5432/bdcdb"``: set the database URI connection.

    - ``BDC_STAC_BASE_URL="http://localhost:5000"``: Base URI of the service.

    - ``BDC_STAC_FILE_ROOT="http://localhost:5001"``: File root for the Assets.

    - ``BDC_STAC_MAX_LIMIT``: Set number of maximum items fetched per request. Default is ``1000``.

    - ``BDC_STAC_TITLE``: Set the catalog title.

    - ``BDC_STAC_ID``: Set the catalog identifier.

To add authentication support with Brazil Data Cube OAuth 2.0, use the following:

    - ``BDC_AUTH_CLIENT_ID``: The OAuth 2.0 client identification

    - ``BDC_AUTH_CLIENT_SECRET``: The OAuth 2.0 client secret

    - ``BDC_AUTH_ACCESS_TOKEN_URL``: The URL domain of BDC-OAuth 2.0 provider.


.. note::

    The parameter ``BDC_STAC_FILE_ROOT`` is used to concat the ``Item asset`` and then generate a display URL
    that will be served by a HTTP Server. In this case, you will need to have a HTTP Server like `NGINX <https://www.nginx.com/>`_
    or `Apache HTTPD <https://httpd.apache.org/>`_.
