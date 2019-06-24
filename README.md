# STAC - SpatioTemporal Asset Catalog Implementation for the Brazil Data Cube

This repository implements a STAC Catalog for the Brazil Data Cube.

## STAC API
The API follows the [STAC.yaml](https://github.com/radiantearth/stac-spec/blob/daeb8c02b8c3301e49aac9e582c2c51272a70997/api-spec/STAC.yaml) file found in the [radiantearth/stac-spec](https://github.com/radiantearth/stac-spec) repository.

## Running
To run the bdc-stac you will need Python 3.7 and install the required packages using:
```bash
pip install -r requirements.txt
```

To use the same data-model you will need Docker and Docker-compose and run the following in the root of this project:
```bash
docker compose up
```

To launch the Flask server:
```bash
FLASK_APP=bdc-stac/indexy flask run
``` 