#
# This file is part of bdc-stac.
# Copyright (C) 2019 INPE.
#
# bdc-stac is a free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
import os

import pytest

os.environ["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:postgres@database:5432/postgres"
os.environ["FILE_ROOT"] = "http://brazildatacube.dpi.inpe.br"

from bdc_stac import create_app


@pytest.fixture(scope="class")
def client():
    app = create_app()
    with app.test_client() as client:
        yield client


class TestBDCStac:
    def test_landing_page(self, client):
        response = client.get("/")

        assert response.status_code == 200

        data = response.get_json()

    def test_conformance(self, client):
        response = client.get("/conformance")

        assert response.status_code == 200

        data = response.get_json()

        assert "conformsTo" in data

    def test_collections(self, client):
        response = client.get("/collections")

        assert response.status_code == 200

        data = response.get_json()

        assert "collections" in data
        assert data["collections"][0]["stac_version"] == "1.0.0-beta.2"
        assert "links" in data

    def test_collection(self, client):
        response = client.get("/collections/CB4_64_16D_STK-1")
        assert response.status_code == 200

        data = response.get_json()

        assert data["id"] == "CB4_64_16D_STK-1"
        assert data["stac_version"] == "1.0.0-beta.2"
        assert data["bdc:grs"] == "BDC_LG"

    def test_collection_items(self, client):
        response = client.get("/collections/CB4_64_16D_STK-1/items?limit=20")

        assert response.status_code == 200

        data = response.get_json()

        assert len(data["features"]) == 20

        feature = data["features"][0]
        assert len(feature["assets"]) > 0
        assert (data["context"]["matched"]) == 5774

    def test_collection_items_id(self, client):
        response = client.get("/collections/CB4_64_16D_STK-1/items/CB4_64_16D_STK_v001_017022_2021-02-02_2021-02-17")

        assert response.status_code == 200

        data = response.get_json()

        assert data["id"] == "CB4_64_16D_STK_v001_017022_2021-02-02_2021-02-17"

    def test_collection_items_id_error(self, client):
        response = client.get("/collections/CB4_64_16D_STK-1/items/wrong_item")

        assert response.status_code == 404

    def test_stac_search(self, client):
        response = client.get("/search")

        assert response.status_code == 200

        data = response.get_json()

        assert (len(data["features"])) == 10

    def test_stac_search_post(self, client):
        response = client.post("/search", content_type="application/json", json=dict())

        assert response.status_code == 200

    def test_stac_search_wrong_content_type(self, client):
        response = client.post("/search", content_type="text/plain", json=dict())

        assert response.status_code == 400

    def test_stac_search_parameters(self, client):
        parameters = {
            "time": "2018-01-01/2020-01-01",
            "page": 1,
            "limit": 1,
            "bbox": [-180, -90, 180, 90],
            "collections": ["CB4_64_16D_STK-1"],
        }

        response = client.post("/search", content_type="application/json", json=parameters)

        assert response.status_code == 200

    def test_stac_search_parameters_ids(self, client):
        parameters = {"ids": ["CB4_64_16D_STK_v001_017022_2021-02-02_2021-02-17"]}

        response = client.post("/search", content_type="application/json", json=parameters)

        assert response.status_code == 200

        data = response.get_json()

        assert data["features"][0]["id"] == "CB4_64_16D_STK_v001_017022_2021-02-02_2021-02-17"

    def test_stac_search_parameters_intersects(self, client):
        parameters = {
            "time": "2018-01-01",
            "intersects": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-122.308150179, 37.488035566],
                        [-122.597502109, 37.538869539],
                        [-122.576687533, 37.613537207],
                        [-122.288048600, 37.562818007],
                        [-122.308150179, 37.488035566],
                    ]
                ],
            },
        }
        response = client.post("/search", content_type="application/json", json=parameters)

        assert response.status_code == 200

    def test_stac_search_parameters_invalid_bbox(self, client):
        parameters = {
            "bbox": [-180, -90, 180, "a"],
        }

        response = client.post("/search", content_type="application/json", json=parameters)

        assert response.status_code == 400
