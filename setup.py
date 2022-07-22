#
# This file is part of Brazil Data Cube STAC Service.
# Copyright (C) 2019-2020 INPE.
#
# Brazil Data Cube STAC Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""STAC Implementation for the Brazil Data Cube."""

import os

from setuptools import find_packages, setup

readme = open("README.rst").read()

history = open("CHANGES.rst").read()

docs_require = [
    "Sphinx>=2.2",
    "sphinx_rtd_theme",
    "sphinx-copybutton",
    "sphinx-tabs",
]

tests_require = [
    "coverage>=4.5",
    "coveralls>=1.8",
    "pytest>=5.2",
    "pytest-cov>=2.8",
    "pytest-pep8>=1.0",
    "pydocstyle>=4.0",
    "isort>4.3",
    "check-manifest>=0.40",
    "black>=19.10a",
    "stac.py>=0.9.0",
]

extras_require = {
    "docs": docs_require,
    "tests": tests_require,
}

extras_require["all"] = [req for exts, reqs in extras_require.items() for req in reqs]

setup_requires = [
    "pytest-runner>=5.2",
]

install_requires = [
    "Flask>=1.1.1",
    "flask-redoc>=0.2.0",
    "GeoAlchemy2>=0.6.3",
    "SQLAlchemy>=1.3,<1.5",
    "Shapely>=1.6",
    "packaging>=20.4",
    "psycopg2-binary>=2.8.4",
    "bdc-catalog @ git+https://github.com/brazil-data-cube/bdc-catalog@v1.0.0-alpha1",
    "bdc-auth-client @ git+https://github.com/brazil-data-cube/bdc-auth-client@v0.4.0",
]

packages = find_packages()

g = {}
with open(os.path.join("bdc_stac", "version.py"), "rt") as fp:
    exec(fp.read(), g)
    version = g["__version__"]

setup(
    name="bdc-stac",
    version=version,
    description=__doc__,
    long_description=readme + "\n\n" + history,
    keywords="STAC RESTful Web Service",
    license="MIT",
    author="Brazil Data Cube Team",
    author_email="brazildatacube@inpe.br",
    url="https://github.com/brazil-data-cube/bdc-stac",
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    entry_points={},
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: GIS",
    ],
)
