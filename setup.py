#
# This file is part of Brazil Data Cube STAC.
# Copyright (C) 2019 INPE.
#
# Brazil Data Cube STAC is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""STAC Implementation for the Brazil Data Cube"""

import os
from setuptools import find_packages, setup

readme = open('README.rst').read()

history = open('CHANGES.rst').read()

docs_require = [
    'Sphinx>=2.2',
]

tests_require = [
    'coverage>=4.5',
    'coveralls>=1.8',
    'pytest>=5.2',
    'pytest-cov>=2.8',
    'pytest-pep8>=1.0',
    'pydocstyle>=4.0',
    'isort>4.3',
    'check-manifest>=0.40',
    'stac @ git+https://github.com/brazil-data-cube/stac.py@b-0.8.1'
]

extras_require = {
    'docs': docs_require,
    'tests': tests_require,
}

extras_require['all'] = [req for exts, reqs in extras_require.items() for req in reqs]

setup_requires = [
    'pytest-runner>=5.2',
]

install_requires = [
    'Flask>=1.1.1',
    'flask-redoc>=0.1.0',
    'GeoAlchemy2>=0.6.3',
    'mgzip>=0.2.1',
    'SQLAlchemy>=1.3.11',
    'psycopg2-binary>=2.8.4',
    'bdc-db @ git+https://github.com/brazil-data-cube/bdc-db@b-0.2',
    'elastic-apm>=5.6.0',
]

packages = find_packages()

g = {}
with open(os.path.join('bdc_stac', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='bdc-stac',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    keywords='STAC RESTful Web Service',
    license='MIT',
    author='INPE',
    author_email='brazildatacube@dpi.inpe.br',
    url='https://github.com/brazil-data-cube/bdc-stac',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: GIS',
    ],
)
