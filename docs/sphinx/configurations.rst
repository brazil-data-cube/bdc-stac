..
    This file is part of Brazil Data Cube STAC Service.
    Copyright (C) 2019-2020 INPE.

    Brazil Data Cube STAC Service is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.


Service Configuration
=====================


.. data:: SQLALCHEMY_DATABASE_URI

   The database URI that should be used for the database connection. Defaults to ``'postgresql://postgres:postgres@localhost:5432/bdc'``.


.. data:: SQLALCHEMY_TRACK_MODIFICATIONS

    Enable (True) or disable (False) signals before and after changes are committed to the database. Defaults to ``False``.


.. data:: SQLALCHEMY_ECHO

   Enables or disable debug output of statements to ``stderr``. Defaults to ``False``.


.. data:: BDC_STAC_BASE_URL

    The base URI of the service. Defaults to ``'http://localhost:5000'``.


.. data:: BDC_STAC_FILE_ROOT

    The prefix for image ``assets``. Defaults to ``'http://localhost:5001'``.


.. data:: BDC_STAC_MAX_LIMIT

    The limit of items returned in a query. Defaults to `1000` (an integer value).


.. data:: BDC_AUTH_CLIENT_SECRET

    **TO BE DONE**. Defaults to ``None``, that means only public collections will be returned.


.. data:: BDC_AUTH_CLIENT_ID

    **TO BE DONE**. Defaults to ``None``, that means only public collections will be returned.


.. data:: BDC_AUTH_ACCESS_TOKEN_URL = os.getenv('BDC_AUTH_ACCESS_TOKEN_URL', None)

    **TO BE DONE**. Defaults to ``None``, that means only public collections will be returned.