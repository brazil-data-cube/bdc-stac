import os

import pytest
import stac

from werkzeug.exceptions import HTTPException

os.environ['DB_HOST'] = "localhost:5432"
os.environ['DB_NAME'] = "bdcdb"
os.environ['DB_USER'] = "postgres"
os.environ['DB_PASS'] = "postgres"
os.environ['API_VERSION'] = "0.7.0"
os.environ['FILE_ROOT'] = "http://brazildatacube.dpi.inpe.br"

from bdc_stac import create_app

@pytest.fixture(scope='class')
def client():
    app = create_app()
    with app.test_client() as client:
        yield client

class TestBDCStac:
    def test_index(self, client):
        response = client.get(
            '/'
        )
        data = response.get_json()

        assert response.status_code == 200
        assert 'docs' in data[1]['href']
        assert 'conformance' in data[2]['href']
        assert 'collections' in data[3]['href']
        assert 'stac' in data[4]['href']
        assert 'stac/search' in data[5]['href']

    def test_conformance(self, client):
        response = client.get(
            '/conformance'
        )
        data = response.get_json()

        assert response.status_code == 200
        assert 'conformsTo' in data

    def test_catalog(self, client):
        response = client.get(
            '/collections'
        )
        data = response.get_json()
        assert response.status_code == 200

        assert stac.Catalog(data, validate=True)
        assert 'stac_version' in data
        assert data['stac_version'] == '0.7.0'
        assert 'id' in data
        assert data['id'] == 'bdc'
        assert 'links' in data
        assert data['links'][1]['title'] == 'LC8SR'
        assert data['links'][2]['title'] == 'S2TOA'

    def test_collection(self, client):
        response = client.get(
            '/collections/LC8SR'
        )
        data = response.get_json()

        assert response.status_code == 200
        assert stac.Collection(data, validate=True)
        assert data['id'] == 'LC8SR'
        assert data['stac_version'] == '0.7.0'
        assert data['properties']['bdc:tiles'][0] == '221069'
        assert data['properties']['bdc:wrs'] == 'WRS2'


    def test_collection_items(self, client):
        response = client.get(
            '/collections/LC8SR/items?limit=1'
        )
        data = response.get_json()

        assert response.status_code == 200
        assert stac.ItemCollection(data, validate=True)
        assert len(data['features']) == 1
        feature = data['features'][0]
        assert stac.ItemCollection(feature, validate=True)
        assert feature['properties']['bdc:tile'] == '221069'
        assert len(feature['assets']) > 0

    def test_collection_items_id(self, client):
        response = client.get(
            '/collections/LC8SR/items/LC8SR-LC08_L1TP_221069_20190103_20190130_01_T1'
        )
        data = response.get_json()

        assert response.status_code == 200
        assert stac.Item(data, validate=True)
        assert data['id'] == 'LC8SR-LC08_L1TP_221069_20190103_20190130_01_T1'

    def test_collection_items_id_error(self, client):
        response = client.get(
            '/collections/LC8SR/items/wrong_item'
        )
        assert response.status_code == 404

    def test_stac_search(self, client):
        response = client.get(
            '/stac/search'
        )
        assert response.status_code == 200

        data = response.get_json()

        assert stac.ItemCollection(data, validate=True)

        response = client.post(
            '/stac/search', content_type='application/json', json=dict()
        )

        assert response.status_code == 200

        data = response.get_json()

        assert stac.ItemCollection(data, validate=True)

    def test_stac_search_wrong_content_type(self, client):
        response = client.post(
            '/stac/search', content_type='text/plain', json=dict()
        )

        assert response.status_code == 400

    def test_stac_search_parameters(self, client):
        parameters = {
            "time": "2018-01-01/2020-01-01",
            "page": 1,
            "limit": 1,
            "bbox":[-180,-90,180,90],
            "collections": ["LC8SR"],
        }

        response = client.post(
            '/stac/search', content_type='application/json', json=parameters
        )

        assert response.status_code == 200

        data = response.get_json()

        assert stac.ItemCollection(data, validate=True)

    def test_stac_search_parameters_ids(self, client):
        parameters = {
            "ids":["LC8SR-LC08_L1TP_221069_20190103_20190130_01_T1"]
        }

        response = client.post(
            '/stac/search', content_type='application/json', json=parameters
        )

        assert response.status_code == 200

        data = response.get_json()

        assert stac.ItemCollection(data, validate=True)

    def test_stac_search_parameters_intersects(self, client):
        parameters = {
            "time": "2018-01-01",
            "intersects":
            {
                "type": "Feature",
                "geometry":
                {
                    "type": "Polygon",
                    "coordinates":
                    [
                        [[-122.308150179, 37.488035566],
                        [-122.597502109, 37.538869539],
                        [-122.576687533, 37.613537207],
                        [-122.288048600, 37.562818007],
                        [-122.308150179, 37.488035566]]
                    ]
                }
            }
        }
        response = client.post(
            '/stac/search', content_type='application/json', json=parameters
        )

        assert response.status_code == 200

        data = response.get_json()

        assert stac.ItemCollection(data, validate=True)

    def test_stac_search_parameters_invalid_bbox(self, client):
        parameters = {
            "bbox":[-180,-90,180,"a"],
        }

        response = client.post(
            '/stac/search', content_type='application/json', json=parameters
        )

        assert response.status_code == 400

