import os
from setuptools import setup, find_packages

readme = open('README.rst').read()

history = open('CHANGES.rst').read()

tests_require = [
    'coverage>=4.5',
    'coveralls>=1.8',
    'pytest>=5.2',
    'pytest-cov>=2.8',
    'pytest-pep8>=1.0',
    'pydocstyle>=4.0',
    'isort>4.3',
    'check-manifest>=0.40'
]

docs_require = [
    'Sphinx>=2.2',
]

extras_require = {
    'docs': docs_require,
    'tests': tests_require,
}

extras_require['all'] = [req for exts, reqs in extras_require.items() for req in reqs]

setup_requires = [
    'pytest-runner>=5.2',
]

with open(os.path.join('bdc_stac', 'version.py'), 'rt') as fp:
    g = {}
    exec(fp.read(), g)
    version = g['__version__']

install_requires = ['Flask==1.1.1',
                    'flasgger==0.9.3',
                    'GeoAlchemy2==0.6.3',
                    'SQLAlchemy==1.3.11',
                    'psycopg2-binary==2.8.4',
                    'git+https://github.com/brazil-data-cube/bdc-db@master',
                    'git+https://github.com/brazil-data-cube/stac.py@master']

packages = find_packages()

setup(
    name='bdc-stac',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    keywords='STAC WebSevice REST',
    license='MIT',
    author='INPE',
    author_email='mzaglia@gmail.com',
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
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3.7',
        'Development Status :: 3 - Alpha',
    ],
)
