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
import os

import pytest
from packaging import version

os.environ["FILE_ROOT"] = "https://brazildatacube.dpi.inpe.br"

from bdc_stac import config, create_app


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
        parsed = version.parse(data["stac_version"])
        assert parsed.base_version == "1.0.0"

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
        assert data["collections"][0]["stac_version"] == config.BDC_STAC_API_VERSION
        assert "links" in data

    def test_collection(self, client):
        response = client.get("/collections/CB4_64_16D_STK-1")
        assert response.status_code == 200

        data = response.get_json()

        assert data["id"] == "CB4_64_16D_STK-1"
        assert data["stac_version"] == config.BDC_STAC_API_VERSION
        assert data["bdc:grs"] == "BDC_LG"
        assert "eo" in data["stac_extensions"]

    def test_collection_items(self, client):
        response = client.get("/collections/CB4_64_16D_STK-1/items?limit=20")

        # TODO: Use JSONSchema validation

        assert response.status_code == 200

        data = response.get_json()

        assert len(data["features"]) == 20
        # Test extension "context"
        assert data["context"]["limit"] == 20 and data["context"]["returned"] == 20

        feature = data["features"][0]
        assert len(feature["assets"]) > 0
        assert (data["context"]["matched"]) > 0

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
        assert response.get_json()["description"] == "[-180, -90, 180, 'a'] is not a valid bbox."
