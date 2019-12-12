import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='bdc_stac',
    version='0.7.0',
    packages=setuptools.find_packages(),
    long_description=long_description,
    include_package_data=True,
    zip_safe=False,
    url="https://github.com/brazil-data-cube/stac",
    install_requires=['Flask==1.1.1',
                      'flasgger==0.9.3',
                      'GeoAlchemy2==0.6.3',
                      'SQLAlchemy==1.3.11',
                      'psycopg2-binary==2.8.4',
                      'git+https://github.com/brazil-data-cube/bdc-db@master',
                      'git+https://github.com/brazil-data-cube/stac.py@master']
)
