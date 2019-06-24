import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='bdc_stac',
    version='1.0.0',
    packages=setuptools.find_packages(),
    long_description=long_description,
    include_package_data=True,
    zip_safe=False,
    url="https://github.com/brazil-data-cube/stac",
    install_requires=['Flask',
                      'flasgger',
                      'sqlalchemy',
                      'mysqlclient',
                      'python-dotenv']
)
