#
# This file is part of bdc-stac.
# Copyright (C) 2019 INPE.
#
# bdc-stac is a free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Routes for the BDC-STAC API."""

import simplejson
import mgzip
import os
from io import BytesIO


from bdc_db import BDCDatabase
from flask import (abort, current_app, jsonify, make_response, request,
                   send_file)
from werkzeug.exceptions import HTTPException, InternalServerError

from .data import (InvalidBoundingBoxError, get_collection,
                   get_collection_items, get_collections, make_geojson,
                   session)

BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')


@current_app.teardown_appcontext
def teardown_appcontext(exceptions=None):
    """Teardown appcontext."""
    session.remove()

@current_app.after_request
def after_request(response):
    """Enable CORS and compress response."""
    response.headers.add('Access-Control-Allow-Origin', '*')

    accept_encoding = request.headers.get('Accept-Encoding', '')

    if response.status_code < 200 or \
        response.status_code >= 300 or \
        response.direct_passthrough or \
        len(response.get_data()) < 500 or \
        'gzip' not in accept_encoding.lower() or \
        'Content-Encoding' in response.headers:
        return response

    compressed_data =  mgzip.compress(response.get_data(), thread=0, compresslevel=4)

    response.set_data(compressed_data)
    response.headers['Content-Encoding'] = 'gzip'
    response.headers['Content-Length'] = len(response.get_data())

    return response

@current_app.route("/", methods=["GET"])
def index():
    """Landing page of this API."""
    links = [{"href": f"{BASE_URL}/", "rel": "self"},
             {"href": f"{BASE_URL}/docs", "rel": "service"},
             {"href": f"{BASE_URL}/conformance", "rel": "conformance"},
             {"href": f"{BASE_URL}/collections", "rel": "data"},
             {"href": f"{BASE_URL}/stac", "rel": "data"},
             {"href": f"{BASE_URL}/stac/search", "rel": "search"}]
    return jsonify(links)


@current_app.route("/conformance", methods=["GET"])
def conformance():
    """Information about standards that this API conforms to."""
    conforms = {"conformsTo": ["http://www.opengis.net/spec/wfs-1/3.0/req/core",
                               "http://www.opengis.net/spec/wfs-1/3.0/req/oas30",
                               "http://www.opengis.net/spec/wfs-1/3.0/req/html",
                               "http://www.opengis.net/spec/wfs-1/3.0/req/geojson"]}
    return jsonify(conforms)

@current_app.route("/collections", methods=["GET"])
@current_app.route("/stac", methods=["GET"])
def root():
    """Return the root catalog or collection."""
    collections = get_collections()
    catalog = dict()
    catalog["description"] = "Brazil Data Cubes Catalog"
    catalog["id"] = "bdc"
    catalog["stac_version"] = os.getenv("API_VERSION", "0.8.1")
    links = list()
    links.append({"href": request.url, "rel": "self"})

    for collection in collections:
        links.append({"href": f"{BASE_URL}/collections/{collection.id}", "rel": "child", "title": collection.id})

    catalog["links"] = links

    return jsonify(catalog)

@current_app.route("/collections/<collection_id>", methods=["GET"])
def collections_id(collection_id):
    """Describe the given feature collection.

    :param collection_id: identifier (name) of a specific collection
    """
    collection = get_collection(collection_id)
    links = [{"href": f"{BASE_URL}/collections/{collection_id}", "rel": "self"},
             {"href": f"{BASE_URL}/collections/{collection_id}/items", "rel": "items"},
             {"href": f"{BASE_URL}/collections", "rel": "parent"},
             {"href": f"{BASE_URL}/collections", "rel": "root"},
             {"href": f"{BASE_URL}/stac", "rel": "root"}]

    collection['links'] = links

    return jsonify(collection)


@current_app.route("/collections/<collection_id>/items", methods=["GET"])
def collection_items(collection_id):
    """Retrieve features of the given feature collection.

    :param collection_id: identifier (name) of a specific collection
    """
    items = get_collection_items(collection_id=collection_id, **request.args.to_dict())

    links = [{"href": f"{BASE_URL}/collections/", "rel": "self"},
             {"href": f"{BASE_URL}/collections/", "rel": "parent"},
             {"href": f"{BASE_URL}/collections/", "rel": "collection"},
             {"href": f"{BASE_URL}/stac", "rel": "root"}]

    gjson = dict()
    gjson['type'] = 'FeatureCollection'

    features = make_geojson(items, links)

    gjson['features'] = features
    return gjson


@current_app.route("/collections/<collection_id>/items/<item_id>", methods=["GET"])
def items_id(collection_id, item_id):
    """Retrieve a given feature from a given feature collection.

    :param collection_id: identifier (name) of a specific collection
    :param item_id: identifier (name) of a specific item
    """
    item = get_collection_items(collection_id=collection_id, item_id=item_id)
    links = [{"href": f"{BASE_URL}/collections/", "rel": "self"},
             {"href": f"{BASE_URL}/collections/", "rel": "parent"},
             {"href": f"{BASE_URL}/collections/", "rel": "collection"},
             {"href": f"{BASE_URL}/stac", "rel": "root"}]

    gjson = make_geojson(item, links)

    if len(gjson) > 0:
        return jsonify(gjson[0])

    abort(404, f"Invalid item id '{item_id}' for collection '{collection_id}'")


@current_app.route("/stac/search", methods=["GET", "POST"])
def stac_search():
    """Search STAC items with simple filtering."""
    bbox, time, ids, collections, page, limit, intersects = None, None, None, None, None, None, None
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

            intersects = request_json.get('intersects', None)

            collections = request_json.get('collections', None)
            collections = request_json.get('ids', None)
            if collections is not None:
                collections = ",".join([x for x in collections])

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

    items = get_collection_items(collections=collections, bbox=bbox,
                                 time=time, ids=ids,
                                 page=page, limit=limit,
                                 intersects=intersects)

    links = [{"href": f"{BASE_URL}/collections/", "rel": "self"},
             {"href": f"{BASE_URL}/collections/", "rel": "parent"},
             {"href": f"{BASE_URL}/collections/", "rel": "collection"},
             {"href": f"{BASE_URL}/stac", "rel": "root"}]

    gjson = dict()
    gjson['type'] = 'FeatureCollection'

    features = make_geojson(items, links)

    gjson['features'] = features

    return jsonify(gjson)

@current_app.errorhandler(Exception)
def handle_exception(e):
    """Handle exceptions."""
    if isinstance(e, HTTPException):
        return {'code': e.code, 'description': e.description}, e.code

    current_app.logger.exception(e)

    return {'code': InternalServerError.code,
            'description': InternalServerError.description}, InternalServerError.code

@current_app.errorhandler(InvalidBoundingBoxError)
def handle_exception(e):
    """Handle InvalidBoundingBoxError."""
    current_app.logger.exception(e)
    resp = jsonify({'code': '400', 'description': str(e)})
    resp.status_code = 400

    return resp
