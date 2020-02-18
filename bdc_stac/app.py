import os
from stac import Catalog, Collection, Item, ItemCollection
from flask import Flask, jsonify, request, abort
from flasgger import Swagger


from bdc_stac.data import get_collection, get_collections, get_collection_items, make_geojson

app = Flask(__name__)

app.config["SWAGGER"] = {
    "openapi": "3.0.1",
    "specs_route": "/docs",
    "title": "Brazil Data Cube Catalog"
}

swagger = Swagger(app, template_file="./spec/api/0.7.0/STAC.yaml")

BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route("/", methods=["GET"])
def index():
    links = [{"href": f"{BASE_URL}/", "rel": "self"},
             {"href": f"{BASE_URL}/docs", "rel": "service"},
             {"href": f"{BASE_URL}/conformance", "rel": "conformance"},
             {"href": f"{BASE_URL}/collections", "rel": "data"},
             {"href": f"{BASE_URL}/stac", "rel": "data"},
             {"href": f"{BASE_URL}/stac/search", "rel": "search"}]
    return jsonify(links)


@app.route("/conformance", methods=["GET"])
def conformance():
    conforms = {"conformsTo": ["http://www.opengis.net/spec/wfs-1/3.0/req/core",
                               "http://www.opengis.net/spec/wfs-1/3.0/req/oas30",
                               "http://www.opengis.net/spec/wfs-1/3.0/req/html",
                               "http://www.opengis.net/spec/wfs-1/3.0/req/geojson"]}
    return jsonify(conforms)


@app.route("/collections/<collection_id>", methods=["GET"])
def collections_id(collection_id):
    collection = get_collection(collection_id)
    links = [{"href": f"{BASE_URL}/collections/{collection_id}", "rel": "self"},
             {"href": f"{BASE_URL}/collections/{collection_id}/items", "rel": "items"},
             {"href": f"{BASE_URL}/collections", "rel": "parent"},
             {"href": f"{BASE_URL}/collections", "rel": "root"},
             {"href": f"{BASE_URL}/stac", "rel": "root"}]

    collection['links'] = links

    return jsonify(Collection(collection, True))


@app.route("/collections/<collection_id>/items", methods=["GET"])
def collection_items(collection_id):
    items = get_collection_items(collection_id=collection_id, **request.args.to_dict())

    links = [{"href": f"{BASE_URL}/collections/", "rel": "self"},
             {"href": f"{BASE_URL}/collections/", "rel": "parent"},
             {"href": f"{BASE_URL}/collections/", "rel": "collection"},
             {"href": f"{BASE_URL}/stac", "rel": "root"}]

    gjson = dict()
    gjson['type'] = 'FeatureCollection'

    features = make_geojson(items, links)

    gjson['features'] = features

    return jsonify(ItemCollection(gjson, True))


@app.route("/collections/<collection_id>/items/<item_id>", methods=["GET"])
def items_id(collection_id, item_id):
    item = get_collection_items(collection_id=collection_id, item_id=item_id)
    links = [{"href": f"{BASE_URL}/collections/", "rel": "self"},
             {"href": f"{BASE_URL}/collections/", "rel": "parent"},
             {"href": f"{BASE_URL}/collections/", "rel": "collection"},
             {"href": f"{BASE_URL}/stac", "rel": "root"}]

    gjson = make_geojson(item, links)

    return jsonify(Item(gjson, True))


@app.route("/collections", methods=["GET"])
@app.route("/stac", methods=["GET"])
def root():
    collections = get_collections()
    catalog = dict()
    catalog["description"] = "Brazil Data Cubes Catalog"
    catalog["id"] = "bdc"
    catalog["stac_version"] = os.getenv("API_VERSION")
    links = list()
    links.append({"href": request.url, "rel": "self"})

    for collection in collections:
        links.append({"href": f"{BASE_URL}/collections/{collection.id}", "rel": "child", "title": collection.id})

    catalog["links"] = links

    return jsonify(Catalog(catalog, True))


@app.route("/stac/search", methods=["GET", "POST"])
def stac_search():
    bbox, time, ids, collections, page, limit = None, None, None, None, None, None
    if request.method == "POST":
        if request.is_json:
            request_json = request.get_json()

            bbox = request_json.get('bbox', None)
            if bbox is not None:
                bbox = ",".join([str(x) for x in bbox])

            time = request_json.get('time', None)

            ids = request_json.get('ids', None)
            if ids is not None:
                ids = ",".join([x for x in ids])

            collections = request_json.get('collections', None)
            cubes = request_json.get('cubes', None)
            page = int(request_json.get('page', 1))
            limit = int(request_json.get('limit', 10))
        else:
            abort(400, "POST Request must be an application/json")

    elif request.method == "GET":
        bbox = request.args.get('bbox', None)
        time = request.args.get('time', None)
        ids = request.args.get('ids', None)
        collections = request.args.get('collections', None)
        cubes = request.args.get('cubes', None)
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))

    items = get_collection_items(collections=collections, bbox=bbox, time=time, ids=ids, page=page, limit=limit)

    links = [{"href": f"{BASE_URL}/collections/", "rel": "self"},
             {"href": f"{BASE_URL}/collections/", "rel": "parent"},
             {"href": f"{BASE_URL}/collections/", "rel": "collection"},
             {"href": f"{BASE_URL}/stac", "rel": "root"}]

    gjson = dict()
    gjson['type'] = 'FeatureCollection'

    features = make_geojson(items, links)

    gjson['features'] = features

    return jsonify(ItemCollection(gjson, True))


@app.errorhandler(400)
def handle_bad_request(e):
    resp = jsonify({'code': '400', 'description': 'Bad Request - {}'.format(e.description)})
    resp.status_code = 400

    return resp


@app.errorhandler(404)
def handle_page_not_found(e):
    resp = jsonify({'code': '404', 'description': 'Page not found'})
    resp.status_code = 404

    return resp


@app.errorhandler(500)
def handle_api_error(e):
    resp = jsonify({'code': '500', 'description': 'Internal Server Error'})
    resp.status_code = 500

    return resp


@app.errorhandler(502)
def handle_bad_gateway_error(e):
    resp = jsonify({'code': '502', 'description': 'Bad Gateway'})
    resp.status_code = 502

    return resp


@app.errorhandler(503)
def handle_service_unavailable_error(e):
    resp = jsonify({'code': '503', 'description': 'Service Unavailable'})
    resp.status_code = 503

    return resp


@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.exception(e)
    resp = jsonify({'code': '500', 'description': 'Internal Server Error'})
    resp.status_code = 500

    return resp


if __name__ == '__main__':
    app.run()
