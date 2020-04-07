..
    This file is part of Brazil Data Cube STAC.
    Copyright (C) 2019 INPE.

    Brazil Data Cube STAC is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.


=======
Changes
=======

Version 0.8.0-0
---------------

Released 2020-04-03

- Support for the SpatioTemporal Asset Catalog (STAC) specification version 0.8.0.
- Database query improvements for fast asset retrieval.
- Based on BDC-DB 0.2.
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
- License: `MIT <https://raw.githubusercontent.com/brazil-data-cube/bdc-db/b-0.2/LICENSE>`_.
- Compatibility with `Brazil Data Cube Database module Version 0.2.0 <https://github.com/brazil-data-cube/bdc-db/tree/v0.2.0>`_.
