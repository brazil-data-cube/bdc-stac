..
    This file is part of Brazil Data Cube STAC Service.
    Copyright (C) 2019-2020 INPE.

    Brazil Data Cube STAC Service is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.


=======
Changes
=======


Version 1.0.0a1 (2022-09-06)
----------------------------

- Implementation of STAC v1.0-rc.1 with the following extensions:

   - `Electro-Optical (eo) <https://github.com/stac-extensions/eo>`_;
   - `SAR <https://github.com/stac-extensions/sar>`_;
   - `Item Assets <https://github.com/stac-extensions/item-assets>`_;
   - `Datacube <https://github.com/stac-extensions/datacube>`_;
   - `Processing <https://github.com/stac-extensions/processing>`_.

- Review the database queries to improve performance
- Improve documentation: Running and deploy `#163 <https://github.com/brazil-data-cube/bdc-stac/issues/163>`_.
- Review unittests


Version 0.9.0-14 (2021-04-01)
-----------------------------

- Improve pagination when using POST in /search (`#141 <https://github.com/brazil-data-cube/bdc-stac/pull/141>`_)
- remove the question mark if there are no args in the url (`#147 <https://github.com/brazil-data-cube/bdc-stac/pull/147>`_)

Version 0.9.0-13 (2021-01-28)
-----------------------------

- Add drone support (`#133 <https://github.com/brazil-data-cube/bdc-stac/issues/133>`_)
- Remove collection metadata from item (`#136 <https://github.com/brazil-data-cube/bdc-stac/issues/136>`_)
- Add missing CORS headers (`#138 <https://github.com/brazil-data-cube/bdc-stac/issues/138>`_)
- Pass auth parameters to asset url (`#130 <https://github.com/brazil-data-cube/bdc-stac/issues/130>`_)
- Fix bug when access collection item id directly (`#140 <https://github.com/brazil-data-cube/bdc-stac/issues/140>`_)

Version 0.9.0-12 (2021-01-14)
-----------------------------

- Add configuration for catalog description and id. (`#129 <https://github.com/brazil-data-cube/bdc-stac/issues/129>`_)

Version 0.9.0-11 (2021-01-05)
-----------------------------


- Display end_datetime in every item. (`#124 <https://github.com/brazil-data-cube/bdc-stac/issues/124>`_)
- Fix datetime filter. (`#127 <https://github.com/brazil-data-cube/bdc-stac/issues/127>`_)


Version 0.9.0-10 (2020-12-01)
-----------------------------

- Add bdc extension schema. (`#89 <https://github.com/brazil-data-cube/bdc-stac/issues/89>`_)
- Add route to serve jsonschemas. (`#90 <https://github.com/brazil-data-cube/bdc-stac/issues/90>`_)
- Add collection_type to collection. (`#120 <https://github.com/brazil-data-cube/bdc-stac/issues/120>`_)
- Fix duplicated item on pagination. (`#121 <https://github.com/brazil-data-cube/bdc-stac/issues/121>`_)


Version 0.9.0-9 (2020-11-23)
-----------------------------

- Use timeline table. (`#87 <https://github.com/brazil-data-cube/bdc-stac/issues/87>`_)
- Fix datetime parameter to work as specified in (`OGC API <http://docs.opengeospatial.org/is/17-069r3/17-069r3.html#_parameter_datetime>`_).
- Improve documentation on datetime parameter (`#114 <https://github.com/brazil-data-cube/bdc-stac/issues/114>`_).


Version 0.9.0-8 (2020-11-16)
----------------------------


- Fix item metadata (`#117 <https://github.com/brazil-data-cube/bdc-stac/pull/117>`_).


Version 0.9.0-7 (2020-11-13)
----------------------------


- Check if platform exists in collection (`#116 <https://github.com/brazil-data-cube/bdc-stac/pull/116>`_).


Version 0.9.0-6 (2020-11-12)
----------------------------


- Display all metadata in collection (`#115 <https://github.com/brazil-data-cube/bdc-stac/pull/115>`_).


Version 0.9.0-5 (2020-10-26)
----------------------------


- Fix collection with no associated grid (`#112 <https://github.com/brazil-data-cube/bdc-stac/pull/112>`_).


Version 0.9.0-4 (2020-10-05)
----------------------------


- Add instrument and platform to collections and items.


Version 0.9.0-3 (2020-09-18)
----------------------------


- Bug fix: Review some links in the service routes (`#110 <https://github.com/brazil-data-cube/bdc-stac/pull/110>`_)



Version 0.9.0-2 (2020-09-11)
----------------------------


- Bug fix: Check if parameter ``bbox`` is valid (an area object) (`#105 <https://github.com/brazil-data-cube/bdc-stac/issues/105>`_)


Version 0.9.0-1 (2020-09-09)
----------------------------


- Bug fix: retrieval of the grid CRS (`#104 <https://github.com/brazil-data-cube/bdc-stac/issues/104>`_)

- Compatibility with `BDC-Catalog data model version 0.6.1 <https://github.com/brazil-data-cube/bdc-catalog>`_.


Version 0.9.0-0 (2020-08-26)
----------------------------


- Optimizations of database queries.

- Review of metadata keys.

- Support for STAC 0.9.0.

- Support for STAC extensions: checksum, commons, context, datacube, eo, version.

- Compatibility with `BDC-Catalog data model version 0.4.0 <https://github.com/brazil-data-cube/bdc-catalog>`_.

- Compatibility with `BDC-Auth-Client version 0.2.1 <https://github.com/brazil-data-cube/bdc-auth-client>`_.

- New Sphinx template.


Version 0.8.1-1 (2020-08-19)
----------------------------


- This is a special version based on STAC 0.8.1 and `BDC Catalog Version 0.4.0 <https://github.com/brazil-data-cube/bdc-catalog/tree/v0.4.0>`_

- Added support for the following STAC Extension: datacube, eo, version.


.. note::

    The tag 0.8.1-0 and below depends on previous version of `BDC Catalog Version 0.2.0 <https://github.com/brazil-data-cube/bdc-catalog/tree/v0.2.0>`_


Version 0.8.1-0 (2020-04-14)
----------------------------


- Support for the SpatioTemporal Asset Catalog (STAC) specification version 0.8.1.

- Compatibility with `Brazil Data Cube Database module Version 0.2.0 <https://github.com/brazil-data-cube/bdc-db/tree/v0.2.0>`_.


Version 0.8.0-0 (2020-04-03)
----------------------------


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


Version 0.7.0-0 (2020-02-21)
----------------------------


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
