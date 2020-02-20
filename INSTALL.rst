..
    This file is part of Brazil Data Cube STAC.
    Copyright (C) 2019 INPE.

    Brazil Data Cube STAC is a free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.


Installation
============

The Brazil Data Cube STAC implementation depends essentially on `Flask <https://palletsprojects.com/p/flask/>`_, `SQLAlchemy <https://www.sqlalchemy.org/>`_, `JSONSchema <https://github.com/Julian/jsonschema>`_ and the `Brazil Data Cube Database Module <https://github.com/brazil-data-cube/bdc-db>`_.


Development Installation
------------------------

Clone the software repository:

.. code-block:: shell

        $ git clone https://github.com/brazil-data-cube/bdc-stac.git


Go to the source code folder:

.. code-block:: shell

        $ cd bdc-stac


Install in development mode:

.. code-block:: shell

        $ pip3 install -e .[all]


Generate the documentation:

.. code-block:: shell

        $ python setup.py build_sphinx


The above command will generate the documentation in HTML and it will place it under:

.. code-block:: shell

    doc/sphinx/_build/html/


Running in Development Mode
---------------------------

In the source code folder, enter the following command:

.. code-block:: shell

        $ FLASK_APP="bdc_stac" \
          FLASK_ENV="development" \
          DB_HOST="localhost:5432" \
          DB_USER="postgres" \
          DB_PASS="secret" \
          DB_NAME="bdcdb" \
          BASE_URI="http://localhost:5000" \
          API_VERSION="0.7.0" \
          FILE_ROOT="http://localhost:5001" \
          flask run


You may need to replace the definition of some environment variables:

    - ``DB_HOST="localhost:5432"``: set the database host address that will be used by the STAC service.

    - ``DB_USER="postgres"``: the user name for connecting to the database server.

    - ``DB_PASS="secret"``: the user password for connecting to the database server.

    - ``DB_NAME="bdcdb"``:  the name of the database containing the image and data cube collections [#f1]_.

    - ``BASE_URI="http://localhost:8080"``: Base URI of the service.

    - ``API_VERSION="0.7.0"``: STAC Version used in the service.

    - ``FILE_ROOT="http://localhost:8081"``: File root for the Assets.



.. rubric:: Footnotes

.. [#f1] Make sure you have a database prepared with the schema for Image and Data Cube collections from the `Brazil Data Cube Database Module <https://github.com/brazil-data-cube/bdc-db>`_

