..
    This file is part of Brazil Data Cube STAC.
    Copyright (C) 2019 INPE.

    Brazil Data Cube STAC is a free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.


Deploying
=========

The Brazil Data Cube STAC implementation depends essentially on `Flask <https://palletsprojects.com/p/flask/>`_, `SQLAlchemy <https://www.sqlalchemy.org/>`_, `JSONSchema <https://github.com/Julian/jsonschema>`_ and the `Brazil Data Cube Database Module <https://github.com/brazil-data-cube/bdc-db>`_.


There is a Dockerfile for quick deployment. This section explains how to get the STAC service up and running with Docker. If you do not have Docker installed, take a look at `this tutorial on how to install it in your system <https://docs.docker.com/install/>`_.



Requirements
------------

Besides Docker, you will need an instance of a PostgreSQL DBMS with a database prepared with the schema for Image and Data Cube collections from the `Brazil Data Cube Database Module <https://github.com/brazil-data-cube/bdc-db>`_.



Building the Docker Image
-------------------------

On the command line use the `docker build` command to create the docker image for the service:

.. code-block:: shell

        $ docker build --no-cache -t bdc-stac:0.8.0-0 .


The above command will create a Docker image named `bdc-stac` and tag `0.8.0-0`, as one can see with the `docker images` command:

.. code-block:: shell

        $ docker images

        REPOSITORY                                          TAG                 IMAGE ID            CREATED             SIZE
        bdc-stac                                            0.8.0-0             44651ac917e4        16 hours ago        333MB


Preparing the Network for Containers
------------------------------------

If you have the PostgreSQL server running in a Docker container and you want to have it accesible to the STAC service, you can create a Docker network and attach your PostgreSQL container to it [#f1]_.

To create a new network, you ca use the `docker network` command:
.. code-block:: shell

        $ docker network create bdc_net


The above command will create a network named `bdc_net`. Now, it is possible to attach your database container in this network:

.. code-block:: shell

        $ docker network connect bdc_net bdc_pg


In the above command, we are supposing that your database container is named `bdc_pg`.


Launching the Docker Container with the STAC Service
----------------------------------------------------

The `docker run` command can be used to launch a container from the image `bdc-stac:0.8.0-0`. The command below shows an example on how to accomplish the launch of a container:

.. code-block:: shell

        $ docker run --detach \
                     --name bdc-stac \
                     --publish 127.0.0.1:8080:5000 \
                     --network=bdc_net \
                     --env DB_HOST="bdc_pg:5432" \
                     --env DB_USER="postgres" \
                     --env DB_PASS="secret" \
                     --env DB_NAME="bdcdb" \
                     --env BASE_URI="http://localhost:8080" \
                     --env API_VERSION="0.8.0" \
                     --env FILE_ROOT="http://localhost:8081" \
                     bdc-stac:0.8.0-0


Let's take a look at each parameter in the above command:/

    - ``--detach``: tells Docker that the container will run in background (daemon).

    - ``--name bdc-stac``: names the container.

    - ``--publish 127.0.0.1:8080:5000``: by default the STAC service will be running on port ``5000`` of the container. You can bind a host port, such as ``8080`` to the container port ``5000``.

    - ``--network=bdc_net``: if the container should connect to the database server through a docker network, this parameter will automatically attach the container to the ``bdc_net``. You can ommit this parameter if the database server address can be resolved directly from a host address.

    - ``--env DB_HOST="bdc_pg:5432"``: set the database host address that will be used by the STAC service. In this example, the name ``bdc_pg`` is the name of a PostgreSQL container in the same network as the STAC service.

    - ``--env DB_USER="postgres"``: the user name for connecting to the database server.

    - ``--env DB_PASS="secret"``: the user password for connecting to the database server.

    - ``--env DB_NAME="bdcdb"``:  the name of the database containing the image and data cube collections [#f2]_.

    - ``--env BASE_URI="http://localhost:8080"``: Base URI of the service.

    - ``--env API_VERSION="0.8.0"``: STAC Version used in the service.

    - ``--env FILE_ROOT="http://localhost:8081"``: File root for the Assets.

    - ``bdc-stac:0.8.0-0``: the name of the base Docker image used to create the container.


If you have launched the container, you can check if the service has initialized:

.. code-block:: shell

        $ docker logs bdc-stac

        * Environment: production
           WARNING: This is a development server. Do not use it in a production deployment.
           Use a production WSGI server instead.
         * Debug mode: off
         * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)


Finally, to test if it is listening, use the ``curl`` command:

.. code-block:: shell

        $ curl localhost:8080

        [{"href":"http://localhost:5000/","rel":"self"},{"href":"http://localhost:5000/docs","rel":"service"},{"href":"http://localhost:5000/conformance","rel":"conformance"},{"href":"http://localhost:5000/collections","rel":"data"},{"href":"http://localhost:5000/stac","rel":"data"},{"href":"http://localhost:5000/stac/search","rel":"search"}]



.. rubric:: Footnotes

.. [#f1] If you have a valid address for the PostgreSQL DBMS you can skip this section.

.. [#f2] Make sure you have a database prepared with the schema for Image and Data Cube collections from the `Brazil Data Cube Database Module <https://github.com/brazil-data-cube/bdc-db>`_

