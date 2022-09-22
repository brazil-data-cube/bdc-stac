#
# This file is part of BDC-STAC.
# Copyright (C) 2022 INPE.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.
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
