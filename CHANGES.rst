..
    This file is part of Brazil Data Cube STAC Service.
    Copyright (C) 2019-2020 INPE.

    Brazil Data Cube STAC Service is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.


=======
Changes
=======


Version 0.9.0-8
---------------

- Fix item metadata (`#117 <https://github.com/brazil-data-cube/bdc-stac/pull/117>`_).

Version 0.9.0-7
---------------

Released 2020-11-13

- Check if platform exists in collection (`#116 <https://github.com/brazil-data-cube/bdc-stac/pull/116>`_).


Version 0.9.0-6
---------------

Released 2020-11-12

- Display all metadata in collection (`#115 <https://github.com/brazil-data-cube/bdc-stac/pull/115>`_).


Version 0.9.0-5
---------------


Released 2020-10-26


- Fix collection with no associated grid (`#112 <https://github.com/brazil-data-cube/bdc-stac/pull/112>`_).


Version 0.9.0-4
---------------


Released 2020-10-05


- Add instrument and platform to collections and items.


Version 0.9.0-3
---------------


Released 2020-09-18


- Bug fix: Review some links in the service routes (`#110 <https://github.com/brazil-data-cube/bdc-stac/pull/110>`_)



Version 0.9.0-2
---------------


Released 2020-09-11


- Bug fix: Check if parameter ``bbox`` is valid (an area object) (`#105 <https://github.com/brazil-data-cube/bdc-stac/issues/105>`_)


Version 0.9.0-1
---------------


Released 2020-09-09


- Bug fix: retrieval of the grid CRS (`#104 <https://github.com/brazil-data-cube/bdc-stac/issues/104>`_)

- Compatibility with `BDC-Catalog data model version 0.6.1 <https://github.com/brazil-data-cube/bdc-catalog>`_.


Version 0.9.0-0
---------------


Released 2020-08-26

- Optimizations of database queries.

- Review of metadata keys.

- Support for STAC 0.9.0.

- Support for STAC extensions: checksum, commons, context, datacube, eo, version.

- Compatibility with `BDC-Catalog data model version 0.4.0 <https://github.com/brazil-data-cube/bdc-catalog>`_.

- Compatibility with `BDC-Auth-Client version 0.2.1 <https://github.com/brazil-data-cube/bdc-auth-client>`_.

- New Sphinx template.


Version 0.8.1-1
---------------


Released 2020-08-19

- This is a special version based on STAC 0.8.1 and `BDC Catalog Version 0.4.0 <https://github.com/brazil-data-cube/bdc-catalog/tree/v0.4.0>`_

- Added support for the following STAC Extension: datacube, eo, version.


.. note::

    The tag 0.8.1-0 and below depends on previous version of `BDC Catalog Version 0.2.0 <https://github.com/brazil-data-cube/bdc-catalog/tree/v0.2.0>`_


Version 0.8.1-0
---------------


Released 2020-04-14

- Support for the SpatioTemporal Asset Catalog (STAC) specification version 0.8.1.

- Compatibility with `Brazil Data Cube Database module Version 0.2.0 <https://github.com/brazil-data-cube/bdc-db/tree/v0.2.0>`_.


Version 0.8.0-0
---------------


Released 2020-04-03

- Support for the SpatioTemporal Asset Catalog (STAC) specification version 0.8.0.

- Database query improvements for fast asset retrieval.

- Compatibility with `Brazil Data Cube Database module Version 0.2.0 <https://github.com/brazil-data-cube/bdc-db/tree/v0.2.0>`_.

- Improved system documentation.

- Improved test system, integration with stac.py version 0.8.

- Improved Travis CI, use of PostgreSQL in the test system.

- Added Zappa scripts for deploying the service in the AWS Lambda.

- More robust implementation.

- Use Flask-Redoc to display online the OpenAPI 3 documentation.

- Added new keys based on BDC metadata: timeline, crs and composite_function.

- Added gunicorn to Dockerfile.


Version 0.7.0-0
---------------


Released 2020-02-21

- First experimental version.

- Support for the SpatioTemporal Asset Catalog (STAC) specification version 0.7.0.

- Support for Brazil Data Cube Image Collections and Data Cube Collections.

- Documentation system based on Sphinx.

- Documentation integrated to ``Read the Docs``.

- Package support through Setuptools.

- Deploy on Docker containers.

- Installation and Deployment instructions.

- Source code versioning based on `Semantic Versioning 2.0.0 <https://semver.org/>`_.

- License: `MIT <https://raw.githubusercontent.com/brazil-data-cube/bdc-stac/v0.7.0-0/LICENSE>`_.

- Compatibility with `Brazil Data Cube Database module Version 0.2.0 <https://github.com/brazil-data-cube/bdc-db/tree/v0.2.0>`_.
