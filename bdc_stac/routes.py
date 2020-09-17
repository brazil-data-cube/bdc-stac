#
# This file is part of bdc-stac.
# Copyright (C) 2019 INPE.
#
# bdc-stac is a free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Routes for the BDC-STAC API."""

import gzip

from bdc_auth_client.decorators import oauth2
from flask import abort, current_app, request
from werkzeug.exceptions import HTTPException, InternalServerError
from werkzeug.urls import url_encode

from .config import BDC_STAC_API_VERSION, BDC_STAC_BASE_URL
from .data import InvalidBoundingBoxError, get_catalog, get_collection_items, get_collections, make_geojson, session

BASE_URL = BDC_STAC_BASE_URL


@current_app.teardown_appcontext
def teardown_appcontext(exceptions=None):
    """Teardown appcontext."""
    session.remove()


@current_app.after_request
def after_request(response):
    """Enable CORS and compress response."""
    response.headers.add("Access-Control-Allow-Origin", "*")

    accept_encoding = request.headers.get("Accept-Encoding", "")

    if (
        response.status_code < 200
        or response.status_code >= 300
        or response.direct_passthrough
        or len(response.get_data()) < 500
        or "gzip" not in accept_encoding.lower()
        or "Content-Encoding" in response.headers
    ):
        return response

    compressed_data = gzip.compress(response.get_data(), compresslevel=4)

    response.set_data(compressed_data)
    response.headers["Content-Encoding"] = "gzip"
    response.headers["Content-Length"] = len(response.get_data())

    return response


@current_app.route("/conformance", methods=["GET"])
def conformance():
    """Information about standards that this API conforms to."""
    return {
        "conformsTo": [
            "http://www.opengis.net/spec/wfs-1/3.0/req/core",
            "http://www.opengis.net/spec/wfs-1/3.0/req/oas30",
            "http://www.opengis.net/spec/wfs-1/3.0/req/html",
            "http://www.opengis.net/spec/wfs-1/3.0/req/geojson",
        ]
    }


@current_app.route("/", methods=["GET"])
@oauth2(required=False, throw_exception=False)
def index(roles=[], access_token=""):
    """Landing page of this API."""
    access_token = f"?access_token={access_token}" if access_token else ""

    collections = get_catalog(roles=roles)
    catalog = dict()
    catalog["description"] = "Brazil Data Cube Catalog"
    catalog["id"] = "bdc"
    catalog["stac_version"] = BDC_STAC_API_VERSION
    links = list()
    links += [
        {"href": f"{BASE_URL}/", "rel": "self", "type": "application/json", "title": "Link to this document"},
        {"href": f"{BASE_URL}/docs", "rel": "service-doc", "type": "text/html", "title": "API documentation in HTML"},
        {
            "href": f"{BASE_URL}/conformance",
            "rel": "conformance",
            "type": "application/json",
            "title": "OGC API conformance classes implemented by the server",
        },
        {
            "href": f"{BASE_URL}/collections",
            "rel": "data",
            "type": "application/json",
            "title": "Information about image collections",
        },
        {"href": f"{BASE_URL}/search", "rel": "search", "type": "application/json", "title": "STAC-Search endpoint"},
    ]

    for collection in collections:
        links.append(
            {
                "href": f"{BASE_URL}/collections/{collection.name}{access_token}",
                "rel": "child",
                "type": "application/json",
                "title": collection.title,
            }
        )

    catalog["links"] = links

    return catalog


@current_app.route("/collections", methods=["GET"])
@oauth2(required=False, throw_exception=False)
def root(roles=[], access_token=""):
    """Return the root catalog or collection."""
    access_token = f"?access_token={access_token}" if access_token else ""

    collections = get_collections(roles=roles)
    response = dict()

    for collection in collections:
        links = [
            {
                "href": f"{BASE_URL}/collections/{collection['id']}{access_token}",
                "rel": "self",
                "type": "application/json",
                "title": "Link to this document",
            },
            {
                "href": f"{BASE_URL}/collections/{collection['id']}/items{access_token}",
                "rel": "items",
                "type": "application/json",
                "title": f"Items of the collection {collection['id']}",
            },
            {
                "href": f"{BASE_URL}/collections{access_token}",
                "rel": "parent",
                "type": "application/json",
                "title": "Link to catalog collections",
            },
            {
                "href": f"{BASE_URL}/{access_token}",
                "rel": "root",
                "type": "application/json",
                "title": "API landing page (root catalog)",
            },
        ]
        collection["links"] = links

    response["collections"] = collections

    return response


@current_app.route("/collections/<collection_id>", methods=["GET"])
@oauth2(required=False, throw_exception=False)
def collections_id(collection_id, roles=[], access_token=""):
    """Describe the given feature collection.

    :param collection_id: identifier (name) of a specific collection
    """
    access_token = f"?access_token={access_token}" if access_token else ""

    collection = get_collections(collection_id, roles=roles)

    if not len(collection) > 0:
        abort(404, "Collection not found.")

    collection = collection[0]

    links = [
        {
            "href": f"{BASE_URL}/collections/{collection['id']}{access_token}",
            "rel": "self",
            "type": "application/json",
            "title": "Link to this document",
        },
        {
            "href": f"{BASE_URL}/collections/{collection['id']}/items{access_token}",
            "rel": "items",
            "type": "application/json",
            "title": f"Items of the collection {collection['id']}",
        },
        {
            "href": f"{BASE_URL}/collections{access_token}",
            "rel": "parent",
            "type": "application/json",
            "title": "Link to catalog collections",
        },
        {
            "href": f"{BASE_URL}/{access_token}",
            "rel": "root",
            "type": "application/json",
            "title": "API landing page (root catalog)",
        },
    ]

    collection["links"] = links

    return collection


@current_app.route("/collections/<collection_id>/items", methods=["GET"])
@oauth2(required=False, throw_exception=False)
def collection_items(collection_id, roles=[], access_token=""):
    """Retrieve features of the given feature collection.

    :param collection_id: identifier (name) of a specific collection
    """
    access_token = f"?access_token={access_token}" if access_token else ""

    items = get_collection_items(collection_id=collection_id, roles=roles, **request.args.to_dict())

    links = [
        {
            "href": f"{BASE_URL}/collections/",
            "rel": "self",
            "type": "application/json",
            "title": "Link to this document",
        },
        {
            "href": f"{BASE_URL}/collections/",
            "rel": "parent",
            "type": "application/json",
            "title": "The collection related to this item",
        },
        {
            "href": f"{BASE_URL}/collections/",
            "rel": "collection",
            "type": "application/json",
            "title": "The collection related to this item",
        },
        {"href": f"{BASE_URL}/", "rel": "root", "type": "application/json", "title": "API landing page (root catalog)"},
    ]

    gjson = dict()
    gjson["stac_version"] = "0.9.0"
    gjson["stac_extensions"] = ["checksum", "commons", "context", "eo"]
    gjson["type"] = "FeatureCollection"

    features = make_geojson(items.items, links, access_token=access_token)

    gjson["links"] = []

    context = dict()
    context["matched"] = items.total
    context["returned"] = len(items.items)
    context["limit"] = items.per_page
    gjson["context"] = context

    args = request.args.copy()
    if items.has_next:
        args["page"] = items.next_num
        gjson["links"].append(
            {"href": f"{BASE_URL}/collections/{collection_id}/items?" + url_encode(args), "rel": "next"}
        )
    if items.has_prev:
        args["page"] = items.prev_num
        gjson["links"].append(
            {"href": f"{BASE_URL}/collections/{collection_id}/items?" + url_encode(args), "rel": "prev"}
        )

    gjson["features"] = features
    return gjson


@current_app.route("/collections/<collection_id>/items/<item_id>", methods=["GET"])
@oauth2(required=False, throw_exception=False)
def items_id(collection_id, item_id, roles=[], access_token=""):
    """Retrieve a given feature from a given feature collection.

    :param collection_id: identifier (name) of a specific collection
    :param item_id: identifier (name) of a specific item
    """
    access_token = f"?access_token={access_token}" if access_token else ""

    item = get_collection_items(collection_id=collection_id, roles=roles, item_id=item_id)
    links = [
        {"href": f"{BASE_URL}/collections/", "rel": "self"},
        {"href": f"{BASE_URL}/collections/", "rel": "parent"},
        {"href": f"{BASE_URL}/collections/", "rel": "collection"},
        {"href": f"{BASE_URL}/", "rel": "root"},
    ]

    gjson = make_geojson(item.items, links, access_token=access_token)

    if len(gjson) > 0:
        return gjson[0]

    abort(404, f"Invalid item id '{item_id}' for collection '{collection_id}'")


@current_app.route("/search", methods=["GET", "POST"])
@oauth2(required=False, throw_exception=False)
def stac_search(roles=[], access_token=""):
    """Search STAC items with simple filtering."""
    access_token = f"?access_token={access_token}" if access_token else ""

    bbox, datetime, ids, collections, page, limit, intersects, query = None, None, None, None, None, None, None, None
    if request.method == "POST":
        if request.is_json:
            request_json = request.get_json()

            bbox = request_json.get("bbox", None)
            if bbox is not None:
                bbox = ",".join([str(x) for x in bbox])

            datetime = request_json.get("datetime", None)

            ids = request_json.get("ids", None)
            if ids is not None:
                ids = ",".join([x for x in ids])

            intersects = request_json.get("intersects", None)
            query = request_json.get("query", None)
            collections = request_json.get("collections", None)
            if collections is not None:
                collections = ",".join([x for x in collections])

            page = int(request_json.get("page", 1))
            limit = int(request_json.get("limit", 10))
        else:
            abort(400, "POST Request must be an application/json")

    elif request.method == "GET":
        bbox = request.args.get("bbox", None)
        datetime = request.args.get("datetime", None)
        ids = request.args.get("ids", None)
        collections = request.args.get("collections", None)
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))

    items = get_collection_items(
        collections=collections,
        roles=roles,
        bbox=bbox,
        datetime=datetime,
        ids=ids,
        page=page,
        limit=limit,
        intersects=intersects,
        query=query,
    )

    links = [
        {"href": f"{BASE_URL}/collections/", "rel": "self"},
        {"href": f"{BASE_URL}/collections/", "rel": "parent"},
        {"href": f"{BASE_URL}/collections/", "rel": "collection"},
        {"href": f"{BASE_URL}/", "rel": "root"},
    ]

    gjson = dict()
    gjson["type"] = "FeatureCollection"

    features = make_geojson(items.items, links, access_token=access_token)

    gjson["links"] = []
    context = dict()
    context["matched"] = items.total
    context["returned"] = len(items.items)
    gjson["context"] = context

    args = request.args.copy()
    if items.has_next:
        args["page"] = items.next_num
        gjson["links"].append({"href": f"{BASE_URL}/search?" + url_encode(args), "rel": "next"})
    if items.has_prev:
        args["page"] = items.prev_num
        gjson["links"].append({"href": f"{BASE_URL}/search?" + url_encode(args), "rel": "prev"})

    gjson["features"] = features

    return gjson


@current_app.errorhandler(Exception)
def handle_exception(e):
    """Handle exceptions."""
    if isinstance(e, HTTPException):
        return {"code": e.code, "description": e.description}, e.code

    current_app.logger.exception(e)

    return {"code": InternalServerError.code, "description": InternalServerError.description}, InternalServerError.code


@current_app.errorhandler(InvalidBoundingBoxError)
def handle_exception_bbox(e):
    """Handle InvalidBoundingBoxError."""
    return {"code": "400", "description": str(e)}, 400
