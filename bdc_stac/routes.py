#
# This file is part of bdc-stac.
# Copyright (C) 2019 INPE.
#
# bdc-stac is a free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Routes for the BDC-STAC API."""

import os
from io import BytesIO

import mgzip
from bdc_db import BDCDatabase
from flask import (abort, current_app, jsonify, make_response, request,
                   send_file)
from werkzeug.exceptions import HTTPException, InternalServerError
from werkzeug.urls import url_encode

from .data import (InvalidBoundingBoxError, get_collection,
                   get_collection_items, get_collections, make_geojson,
                   session)

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

    compressed_data = mgzip.compress(
        response.get_data(), thread=0, compresslevel=4)

    response.set_data(compressed_data)
    response.headers['Content-Encoding'] = 'gzip'
    response.headers['Content-Length'] = len(response.get_data())

    return response


@current_app.route("/", methods=["GET"])
def index():
    """Landing page of this API."""
    return jsonify([{"href": f"{request.url_root}", "rel": "self"},
                    {"href": f"{request.url_root}docs", "rel": "service"},
                    {"href": f"{request.url_root}conformance", "rel": "conformance"},
                    {"href": f"{request.url_root}collections", "rel": "data"},
                    {"href": f"{request.url_root}stac", "rel": "data"},
                    {"href": f"{request.url_root}stac/search", "rel": "search"}])

@current_app.route("/conformance", methods=["GET"])
def conformance():
    """Information about standards that this API conforms to."""
    return {"conformsTo": ["http://www.opengis.net/spec/wfs-1/3.0/req/core",
                           "http://www.opengis.net/spec/wfs-1/3.0/req/oas30",
                           "http://www.opengis.net/spec/wfs-1/3.0/req/html",
                           "http://www.opengis.net/spec/wfs-1/3.0/req/geojson"]}


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
        links.append({"href": f"{request.url_root}collections/{collection.id}",
                      "rel": "child", "title": collection.id})

    catalog["links"] = links

    return catalog


@current_app.route("/collections/<collection_id>", methods=["GET"])
def collections_id(collection_id):
    """Describe the given feature collection.

    :param collection_id: identifier (name) of a specific collection
    """
    collection = get_collection(collection_id)
    links = [{"href": f"{request.url_root}collections/{collection_id}", "rel": "self"},
             {"href": f"{request.url_root}collections/{collection_id}/items", "rel": "items"},
             {"href": f"{request.url_root}collections", "rel": "parent"},
             {"href": f"{request.url_root}collections", "rel": "root"},
             {"href": f"{request.url_root}stac", "rel": "root"}]

    collection['links'] = links

    return collection


@current_app.route("/collections/<collection_id>/items", methods=["GET"])
def collection_items(collection_id):
    """Retrieve features of the given feature collection.

    :param collection_id: identifier (name) of a specific collection
    """
    items = get_collection_items(
        collection_id=collection_id, **request.args.to_dict())

    links = [{"href": f"{request.url_root}collections/", "rel": "self"},
             {"href": f"{request.url_root}collections/", "rel": "parent"},
             {"href": f"{request.url_root}collections/", "rel": "collection"},
             {"href": f"{request.url_root}stac", "rel": "root"}]

    gjson = dict()
    gjson['type'] = 'FeatureCollection'

    features = make_geojson(items.items, links)

    gjson['links'] = []

    gjson['numberMatched'] = items.total
    gjson['numberReturned'] = len(items.items)

    args = request.args.copy()
    if items.has_next:
        args['page'] = items.next_num
        gjson['links'].append(
            {"href": f"{request.url_root}collections/{collection_id}/items?"+url_encode(args), "rel": "next"})
    if items.has_prev:
        args['page'] = items.prev_num
        gjson['links'].append(
            {"href": f"{request.url_root}collections/{collection_id}/items?"+url_encode(args), "rel": "prev"})

    gjson['features'] = features
    return gjson


@current_app.route("/collections/<collection_id>/items/<item_id>", methods=["GET"])
def items_id(collection_id, item_id):
    """Retrieve a given feature from a given feature collection.

    :param collection_id: identifier (name) of a specific collection
    :param item_id: identifier (name) of a specific item
    """
    item = get_collection_items(collection_id=collection_id, item_id=item_id)
    links = [{"href": f"{request.url_root}collections/", "rel": "self"},
             {"href": f"{request.url_root}collections/", "rel": "parent"},
             {"href": f"{request.url_root}collections/", "rel": "collection"},
             {"href": f"{request.url_root}stac", "rel": "root"}]

    gjson = make_geojson(item.items, links)

    if len(gjson) > 0:
        return gjson[0]

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

    links = [{"href": f"{request.url_root}collections/", "rel": "self"},
             {"href": f"{request.url_root}collections/", "rel": "parent"},
             {"href": f"{request.url_root}collections/", "rel": "collection"},
             {"href": f"{request.url_root}stac", "rel": "root"}]

    gjson = dict()
    gjson['type'] = 'FeatureCollection'

    features = make_geojson(items.items, links)

    gjson['links'] = []

    gjson['numberMatched'] = items.total
    gjson['numberReturned'] = len(items.items)

    args = request.args.copy()
    if items.has_next:
        args['page'] = items.next_num
        gjson['links'].append(
            {"href": f"{request.url_root}stac/search?"+url_encode(args), "rel": "next"})
    if items.has_prev:
        args['page'] = items.prev_num
        gjson['links'].append(
            {"href": f"{request.url_root}stac/search?"+url_encode(args), "rel": "prev"})

    gjson['features'] = features

    return gjson


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
    return {'code': '400', 'description': str(e)}, 400
