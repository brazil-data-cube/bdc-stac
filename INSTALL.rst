..
    This file is part of Brazil Data Cube STAC.
    Copyright (C) 2019 INPE.

    Brazil Data Cube STAC is a free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.


Installation
============


Development Installation
------------------------


Pre-Requirements
++++++++++++++++


The Brazil Data Cube STAC implementation depends essentially on:

- `Flask <https://palletsprojects.com/p/flask/>`_: a lightweight WSGI web application framework.

- `Flask-SQLAlchemy <https://flask-sqlalchemy.palletsprojects.com/en/2.x/>`_: an extension for Flask that adds support of `SQLAlchemy <https://www.sqlalchemy.org/>`_.

- `BDC-Catalog <https://bdc-catalog.readthedocs.io/en/latest/>`_: an image metadata storage module for Earth Observation imagery of Brazil Data Cube.

- `Flask-Redoc <https://pypi.org/project/flask-redoc/>`_: a Flask extension for displaying OpenAPI/Swagger documentation using Redocs.


Clone the software repository
+++++++++++++++++++++++++++++

Use ``git`` to clone the software repository::

    git clone https://github.com/brazil-data-cube/bdc-stac.git


Install BDC-STAC in Development Mode
++++++++++++++++++++++++++++++++++++

Go to the source code folder::

        $ cd bdc-stac


Install in development mode::

        $ pip3 install -e .[all]


.. note::

    If you want to create a new *Python Virtual Environment*, please, follow this instruction:

    *1.* Create a new virtual environment linked to Python 3.7::

        python3.7 -m venv venv


    **2.** Activate the new environment::

        source venv/bin/activate


    **3.** Update pip and setuptools::

        pip3 install --upgrade pip

        pip3 install --upgrade setuptools


Build the Documentation
+++++++++++++++++++++++


You can generate the documentation based on Sphinx with the following command::

    python setup.py build_sphinx


The above command will generate the documentation in HTML and it will place it under::

    docs/sphinx/_build/html/


You can open the above documentation in your favorite browser, as::

    firefox docs/sphinx/_build/html/index.html


Running in Development Mode
---------------------------

.. note::

        Make sure you have a database prepared using `Brazil Data Cube Catalog Module <https://github.com/brazil-data-cube/bdc-catalog>`_.


In the source code folder, enter the following command:

.. code-block:: shell

        $ FLASK_APP="bdc_stac" \
          FLASK_ENV="development" \
          SQLALCHEMY_DATABASE_URI="postgresql://postgres:secret@localhost:54320/bdc_new" \
          BDC_STAC_BASE_URI="http://localhost:5000" \
          BDC_STAC_API_VERSION="0.8.1" \
          BDC_STAC_FILE_ROOT="http://localhost:5001" \
          flask run


You may need to replace the definition of some environment variables:

    - ``SQLALCHEMY_DATABASE_URI="postgresql://postgres:secret@localhost:5432/bdcdb"``: set the database host address that will be used by the STAC service.

    - ``BDC_STAC_BASE_URI="http://localhost:8080"``: Base URI of the service.

    - ``BDC_STAC_API_VERSION="0.8.1"``: STAC Version used in the service.

    - ``BDC_STAC_FILE_ROOT="http://localhost:8081"``: File root for the Assets.

    - ``BDC_STAC_MAX_LIMIT``: Set number of maximum items fetched per request. Default is ``1000``.

To add authentication support with Brazil Data Cube OAuth 2.0, use the following:

    - ``BDC_AUTH_CLIENT_ID``: The OAuth 2.0 client identification

    - ``BDC_AUTH_CLIENT_SECRET``: The OAuth 2.0 client secret

    - ``BDC_AUTH_ACCESS_TOKEN_URL``: The URL domain of BDC-OAuth 2.0 provider.


.. note::

        If you would like to set database URI connection individually instead ``SQLALCHEMY_DATABASE_URI``, you can also set:

            - ``DB_HOST`` - the host address
            - ``DB_NAME`` - the database name
            - ``DB_USER`` - as user name connection
            - ``DB_PASS`` - the user password
