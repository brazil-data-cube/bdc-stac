from flask import Flask, jsonify, request, abort
from flasgger import Swagger
from dotenv import load_dotenv, find_dotenv
import os
from bdc_stac import data

load_dotenv(find_dotenv())

app = Flask(__name__)

app.config["JSON_SORT_KEYS"] = False
app.config["SWAGGER"] = {
    "openapi": "3.0.1",
    "specs_route": "/docs",
    "title": "Brazil Data Cubes Catalog"
}

swagger = Swagger(app, template_file="./spec/api/v0.7/STAC.yaml")


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route("/", methods=["GET"])
def index():
    links = [{"href": f"{request.url_root}", "rel": "self"},
             {"href": f"{request.url_root}docs", "rel": "service"},
             {"href": f"{request.url_root}conformance", "rel": "conformance"},
             {"href": f"{request.url_root}collections", "rel": "data"},
             {"href": f"{request.url_root}stac", "rel": "data"}]
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
    collection = data.get_collection(collection_id)
    links = [{"href": f"{request.url_root}collections/{collection_id}", "rel": "self"},
             {"href": f"{request.url_root}collections/{collection_id}/items", "rel": "items"},
             {"href": f"{request.url_root}collections", "rel": "parent"},
             {"href": f"{request.url_root}collections", "rel": "root"},
             {"href": f"{request.url_root}stac", "rel": "root"}]

    collection['links'] = links

    return jsonify(collection)


@app.route("/collections/<collection_id>/items", methods=["GET"])
def collection_items(collection_id):
    items = data.get_collection_items(collection_id=collection_id, bbox=request.args.get('bbox', None),
                                      time=request.args.get('time', None))

    links = [{"href": f"{request.url_root}collections/", "rel": "self"},
             {"href": f"{request.url_root}collections/", "rel": "parent"},
             {"href": f"{request.url_root}collections/", "rel": "collection"},
             {"href": f"{request.url_root}stac", "rel": "root"}]

    gjson = data.make_geojson(items, links, page=int(request.args.get('page', 1)),
                              limit=int(request.args.get('limit', 10)))

    return jsonify(gjson)


@app.route("/collections/<collection_id>/items/<item_id>", methods=["GET"])
def items_id(collection_id, item_id):
    item = data.get_collection_items(collection_id=collection_id, item_id=item_id)
    links = [{"href": f"{request.url_root}collections/", "rel": "self"},
             {"href": f"{request.url_root}collections/", "rel": "parent"},
             {"href": f"{request.url_root}collections/", "rel": "collection"},
             {"href": f"{request.url_root}stac", "rel": "root"}]

    gjson = data.make_geojson(item, links)

    return jsonify(gjson)


@app.route("/collections", methods=["GET"])
@app.route("/stac", methods=["GET"])
def stac():
    datacubes = data.get_collections()
    catalog = dict()
    catalog["description"] = "Brazil Data Cubes Catalog"
    catalog["id"] = "bdc"
    catalog["stac_version"] = os.getenv("API_VERSION")
    links = list()
    links.append({"href": request.url, "rel": "self"})

    for datacube in datacubes:
        links.append({"href": f"{request.url_root}collections/{datacube['datacube']}", "rel": "child"})

    catalog["links"] = links

    return jsonify(catalog)


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
            if collections is not None:
                collections = ",".join([x for x in collections])

            page = int(request_json.get('page', 1))
            limit = int(request_json.get('limit', 10))
        else:
            abort(400, "POST Request must be an application/json")

    elif request.method == "GET":
        bbox = request.args.get('bbox', None)
        time = request.args.get('time', None)
        ids = request.args.get('ids', None)
        collections = request.args.get('collections', None)
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))

    items = data.get_collection_items(collections=collections, bbox=bbox, time=time, ids=ids)

    links = [{"href": f"{request.url_root}collections/", "rel": "self"},
             {"href": f"{request.url_root}collections/", "rel": "parent"},
             {"href": f"{request.url_root}collections/", "rel": "collection"},
             {"href": f"{request.url_root}stac", "rel": "root"}]

    gjson = data.make_geojson(items, links=links, page=page, limit=limit)

    return jsonify(gjson)


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
