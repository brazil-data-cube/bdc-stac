from unittest.mock import Mock, patch

import jsonschema
import pytest

from bdc_stac.app import app

class TestBDCStac:
    def test_index(self):
        response = app.test_client().get(
            '/'
        )
        data = response.get_json()

        assert response.status_code == 200
        assert 'docs' in data[1]['href']
        assert 'conformance' in data[2]['href']
        assert 'collections' in data[3]['href']
        assert 'stac' in data[4]['href']
        assert 'stac/search' in data[5]['href']

    def test_catalog(self, mock_data):
        pass

    def test_collection(self):
        pass

    def test_collection_items(self):
        pass

    def test_collection_items_id(self):
        pass

    def test_stac(self):
        pass

    def test_stac_search(self):
        pass



if __name__ == '__main__':
    pytest.main(['--color=auto', '--no-cov'])