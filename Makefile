#
# This file is part of Brazil Data Cube STAC Service.
# Copyright (C) 2019-2020 INPE.
#
# Brazil Data Cube STAC Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

SHELL := /bin/bash

.PHONY: all tests docs doc

tests:
	pydocstyle bdc_stac && \
	isort --check-only --diff --recursive bdc_stac/*.py && \
	check-manifest --ignore ".travis-*" --ignore ".readthedocs.*" && \
	pytest && \
	sphinx-build -qnW --color -b doctest doc/sphinx/ doc/sphinx/_build/doctest

docs:
	sphinx-apidoc -o doc/sphinx bdc_stac

.ONESHELL:
before_install:
	pip install --upgrade pip
	pip install --upgrade setuptools
	docker run --name bdc-pg -p 127.0.0.1:5432:5432 -e POSTGRES_PASSWORD=postgres -d postgis/postgis:12-3.0
	virtualenv venv -p python3
	source venv/bin/activate
	git clone -b b-0.2 --depth 1 https://github.com/brazil-data-cube/bdc-db
	cd bdc-db
	pip install .
	bdc-db db create-db
	bdc-db db upgrade
	bdc-db db migrate
	bdc-db fixtures init
	deactivate
	cd ..
	rm -rf bdc-db
	source ~/virtualenv/python3.7/bin/activate

install:
	pip install -e .[tests,docs]

deploy:
	pip install zappa
	zappa update
