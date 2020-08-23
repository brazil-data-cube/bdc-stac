#!/usr/bin/env bash
#
# This file is part of Brazil Data Cube STAC Service.
# Copyright (C) 2019-2020 INPE.
#
# Brazil Data Cube STAC Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

pydocstyle bdc_stac tests setup.py && \
isort bdc_stac tests setup.py --check-only --diff && \
check-manifest --ignore ".travis-*" --ignore ".readthedocs.*" && \
sphinx-build -qnW --color -b doctest docs/sphinx/ docs/sphinx/_build/doctest  && \
pytest