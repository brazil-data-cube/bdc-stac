..
    This file is part of Brazil Data Cube STAC Service.
    Copyright (C) 2019-2022 INPE.

    Brazil Data Cube STAC Service is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.


Deploying
=========


There is a Dockerfile for quick deployment. This section explains how to get the STAC service up and running with Docker. If you do not have Docker installed, take a look at `this tutorial on how to install it in your system <https://docs.docker.com/install/>`_.



Requirements
------------


Besides Docker, you will need an instance of a PostgreSQL DBMS with a database prepared using `Brazil Data Cube Catalog Module <https://github.com/brazil-data-cube/bdc-catalog>`_.
Before prepare database instance, just take a look in support mapping of BDC-STAC:

- STAC ``v0.9.0``  -> ``BDC-Catalog 0.8.x``
- STAC ``v1.0.0+`` -> ``BDC-Catalog 1.0+``


Building the Docker Image
-------------------------


On the command line use the ``docker build`` command to create the docker image for the service::

    docker build --no-cache -t bdc-stac:1.0.0 .


The above command will create a Docker image named ``bdc-stac`` and tag ``0.9.0-0`, as one can see with the ``docker images`` command::

    docker images

    REPOSITORY                                          TAG                 IMAGE ID            CREATED             SIZE
    bdc-stac                                            1.0.0             44651ac917e4        16 hours ago        333MB


Preparing the Network for Containers
------------------------------------


If you have the PostgreSQL server running in a Docker container and you want to have it accessible to the STAC service, you can create a Docker network and attach your PostgreSQL container to it.


.. note::

    If you have a valid address for the PostgreSQL DBMS you can skip this section.


To create a new network, you ca use the ``docker network`` command::

    docker network create bdc_net


The above command will create a network named ``bdc_net``. Now, it is possible to attach your database container in this network::

    docker network connect bdc_net bdc_pg


In the previous command, we are supposing that your database container is named ``bdc_pg``.


Launching the Docker Container with the STAC Service
----------------------------------------------------


The ``docker run`` command can be used to launch a container from the image ``bdc-stac:0.9.0-0``. The command below shows an example on how to accomplish the launch of a container::

    docker run --detach \
               --name bdc-stac \
               --publish 127.0.0.1:8080:5000 \
               --network=bdc_net \
               --env SQLALCHEMY_DATABASE_URI="postgresql://postgres:postgres@localhost:5432/bdc_catalog" \
               --env BDC_STAC_BASE_URL="http://localhost:8080" \
               --env BDC_STAC_FILE_ROOT="http://localhost:8081" \
               bdc-stac:1.0.0


Let's take a look at each parameter in the above command:

    - ``--detach``: tells Docker that the container will run in background (daemon).

    - ``--name bdc-stac``: names the container.

    - ``--publish 127.0.0.1:8080:5000``: by default the STAC service will be running on port ``5000`` of the container. You can bind a host port, such as ``8080`` to the container port ``5000``.

    - ``--network=bdc_net``: if the container should connect to the database server through a docker network, this parameter will automatically attach the container to the ``bdc_net``. You can omit this parameter if the database server address can be resolved directly from a host address.

    - ``--env SQLALCHEMY_DATABASE_URI="postgresql://postgres:postgres@localhost:5432/bdc_catalog"``: set the database URI.\ [#f1]_.

    - ``--env BDC_STAC_BASE_URL="http://localhost:8080"``: Base URI of the service.

    - ``--env BDC_STAC_FILE_ROOT="http://localhost:8081"``: File root for the image ``assets``.

    - ``bdc-stac:1.0.0``: the name of the base Docker image used to create the container.


If you have launched the container, you can check if the service has initialized::

    docker logs bdc-stac

    * Environment: production
       WARNING: This is a development server. Do not use it in a production deployment.
       Use a production WSGI server instead.
     * Debug mode: off
     * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)


Finally, to test if it is listening, use the ``curl`` command::

    $ curl localhost:8080


The output should be a JSON document similar to:


.. code-block:: json

    {
        "type": "Catalog",
        "description": "Brazil Data Cube Catalog",
        "id": "bdc",
        "stac_version": "1.0.0-rc.1",
        "links": [
            {
                "href": "http://localhost:8080/",
                "rel": "self",
                "type": "application/json",
                "title": "Link to this document"
            },
            {
                "href": "http://localhost:8080/docs",
                "rel": "service-doc",
                "type": "text/html",
                "title": "API documentation in HTML"
            },
            {
                "href": "http://localhost:8080/conformance",
                "rel": "conformance",
                "type": "application/json",
                "title": "OGC API conformance classes implemented by the server"
            },
            {
                "href": "http://localhost:8080/collections",
                "rel": "data",
                "type": "application/json",
                "title": "Information about image collections"
            },
            {
                "href": "http://localhost:8080/search",
                "rel": "search",
                "type": "application/geo+json",
                "title": "STAC-Search endpoint"
            },
            {
                "href": "http://localhost:8080/collections/MOD13Q1-6",
                "rel": "child",
                "type": "application/json",
                "title": "TERRA - MODIS - MOD13Q1 - C6"
            },
            {
                "href": "http://localhost:8080/collections/MYD13Q1-6",
                "rel": "child",
                "type": "application/json",
                "title": "AQUA - MODIS - MYD13Q1 - C6"
            },
            {
                "href": "http://localhost:8080/collections/S2_L1C-1",
                "rel": "child",
                "type": "application/json",
                "title": "Sentinel-2 - MSI - Level-1C"
            }
        ],
        "conformsTo": [
            "https://api.stacspec.org/v1.0.0-beta.1/core",
            "https://api.stacspec.org/v1.0.0-beta.1/item-search",
            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core",
            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/oas30",
            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson"
        ]
    }


.. rubric:: Footnotes

.. [#f1] See the `Brazil Data Cube Catalog Module <https://github.com/brazil-data-cube/bdc-catalog>`_.