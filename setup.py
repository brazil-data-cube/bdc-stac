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
    # Remove Flask 2.3 limitation due warnings related dependencies (flask-redoc)
    "Flask>=1.1.1,<2.3",
    "flask-redoc>=0.2.0",
    "Flask-SQLAlchemy>=2.4,<3",
    "GeoAlchemy2>=0.6.3",
    "SQLAlchemy>=1.3,<1.5",
    "Shapely>=1.6",
    "packaging>=20.4",
    "psycopg2-binary>=2.8.4",
    "bdc-catalog @ git+https://github.com/brazil-data-cube/bdc-catalog@v1.0.0",
    "bdc-auth-client @ git+https://github.com/brazil-data-cube/bdc-auth-client@v0.4.2",
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
    license="GPLv3",
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
        "License :: OSI Approved :: GPL v3 License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: GIS",
    ],
)
