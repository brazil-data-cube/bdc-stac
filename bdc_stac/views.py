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

from .config import BDC_STAC_API_VERSION, BDC_STAC_ASSETS_ARGS, BDC_STAC_BASE_URL, BDC_STAC_ID, BDC_STAC_TITLE
from .controller import get_catalog, get_collection_items, get_collections, make_geojson, session


@current_app.teardown_appcontext
def teardown_appcontext(exceptions=None):
    """Teardown appcontext."""
    session.remove()


@current_app.before_request
def before_request():
    """Handle for before request processing."""
    request.assets_kwargs = None

    if BDC_STAC_ASSETS_ARGS:
        assets_kwargs = {arg: request.args.get(arg) for arg in BDC_STAC_ASSETS_ARGS.split(",")}
        if "access_token" in request.args:
            assets_kwargs["access_token"] = request.args.get("access_token")
        assets_kwargs = "?" + url_encode(assets_kwargs) if url_encode(assets_kwargs) else ""
        request.assets_kwargs = assets_kwargs


@current_app.after_request
def after_request(response):
    """Enable CORS and compress response."""
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST")

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
@oauth2(required=False)
def index(roles=None):
    """Landing page of this API."""
    catalog = get_catalog(roles=roles)

    links = [
        {"href": f"{BDC_STAC_BASE_URL}/", "rel": "self", "type": "application/json", "title": "Link to this document"},
        {
            "href": f"{BDC_STAC_BASE_URL}/docs",
            "rel": "service-doc",
            "type": "text/html",
            "title": "API documentation in HTML",
        },
        {
            "href": f"{BDC_STAC_BASE_URL}/conformance",
            "rel": "conformance",
            "type": "application/json",
            "title": "OGC API conformance classes implemented by the server",
        },
        {
            "href": f"{BDC_STAC_BASE_URL}/collections",
            "rel": "data",
            "type": "application/json",
            "title": "Information about image collections",
        },
        {
            "href": f"{BDC_STAC_BASE_URL}/search",
            "rel": "search",
            "type": "application/json",
            "title": "STAC-Search endpoint",
        },
    ]

    for collection in catalog:
        links.append(
            {
                "href": f"{BDC_STAC_BASE_URL}/collections/{collection.name}{request.assets_kwargs}",
                "rel": "child",
                "type": "application/json",
                "title": collection.title,
            }
        )

    return {
        "description": BDC_STAC_TITLE,
        "id": BDC_STAC_ID,
        "stac_version": BDC_STAC_API_VERSION,
        "links": links,
        "conformsTo": [
            "https://api.stacspec.org/v1.0.0-beta.1/core",
            "https://api.stacspec.org/v1.0.0-beta.1/item-search",
            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core",
            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/oas30",
            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson",
        ],
    }


@current_app.route("/collections", methods=["GET"])
@oauth2(required=False)
def root(roles=None):
    """Object with a list of Collections contained in the catalog and links."""
    collections = get_collections(roles=roles, assets_kwargs=request.assets_kwargs)

    links = [
        {
            "href": f"{BDC_STAC_BASE_URL}/",
            "rel": "root",
            "type": "application/json",
            "title": "Link to the root catalog.",
        },
        {
            "href": f"{BDC_STAC_BASE_URL}/collections",
            "rel": "self",
            "type": "application/json",
            "title": "Link to this document",
        },
    ]

    return {"collections": collections, "links": links}


@current_app.route("/collections/<collection_id>", methods=["GET"])
@oauth2(required=False)
def collections_id(collection_id, roles=None):
    """Describe the given feature collection.

    :param collection_id: identifier (name) of a specific collection
    """
    collection = get_collections(collection_id, roles=roles, assets_kwargs=request.assets_kwargs)

    if not len(collection):
        abort(404, "Collection not found.")

    return collection[0]


@current_app.route("/collections/<collection_id>/items", methods=["GET"])
@oauth2(required=False)
def collection_items(collection_id, roles=None):
    """Retrieve features of the given feature collection.

    :param collection_id: identifier (name) of a specific collection
    """
    items = get_collection_items(collection_id=collection_id, roles=roles, **request.args)

    features = make_geojson(items.items, assets_kwargs=request.assets_kwargs)

    item_collection = {
        "stac_version": BDC_STAC_API_VERSION,
        "stac_extensions": ["checksum", "commons", "context", "eo"],
        "type": "FeatureCollection",
        "links": [],
        "context": {"matched": items.total, "returned": len(items.items), "limit": items.per_page},
        "features": features,
    }

    args = request.args.copy()

    if items.has_next:
        args["page"] = items.next_num
        item_collection["links"].append(
            {
                "href": f"{BDC_STAC_BASE_URL}/collections/{collection_id}/items{f'?{url_encode(args)}' if len(args) > 0 else ''}",
                "rel": "next",
            }
        )
    if items.has_prev:
        args["page"] = items.prev_num
        item_collection["links"].append(
            {
                "href": f"{BDC_STAC_BASE_URL}/collections/{collection_id}/items{f'?{url_encode(args)}' if len(args) > 0 else ''}",
                "rel": "prev",
            }
        )

    return item_collection


@current_app.route("/collections/<collection_id>/items/<item_id>", methods=["GET"])
@oauth2(required=False)
def items_id(collection_id, item_id, roles=None):
    """Retrieve a given feature from a given feature collection.

    :param collection_id: identifier (name) of a specific collection
    :param item_id: identifier (name) of a specific item
    """
    item = get_collection_items(collection_id=collection_id, roles=roles, item_id=item_id)

    if not item.total:
        abort(404, f"Invalid item id '{item_id}' for collection '{collection_id}'")

    item = make_geojson(item.items, assets_kwargs=request.assets_kwargs)[0]

    return item


@current_app.route("/search", methods=["POST"])
@oauth2(required=False)
def stac_search_post(roles=None):
    """Search STAC items with simple filtering."""
    assets_kwargs = None

    if request.is_json:
        items = get_collection_items(**request.json, roles=roles)
    else:
        abort(400, "POST Request must be an application/json")

    features = make_geojson(items.items, assets_kwargs=request.assets_kwargs)

    response = {
        "type": "FeatureCollection",
        "links": [],
        "context": {
            "matched": items.total,
            "returned": len(items.items),
        },
        "features": features,
    }
    if items.has_next:
        next_links = {
            "href": f"{BDC_STAC_BASE_URL}/search{assets_kwargs}",
            "rel": "next",
        }

        next_links["body"] = request.json.copy()
        next_links["body"]["page"] = items.next_num
        next_links["method"] = "POST"
        next_links["merge"] = True

    if items.has_prev:
        prev_links = {
            "href": f"{BDC_STAC_BASE_URL}/search{assets_kwargs}",
            "rel": "prev",
        }

        prev_links["body"] = request.json.copy()
        prev_links["body"]["page"] = items.prev_num
        prev_links["method"] = "POST"
        prev_links["merge"] = True
        response["links"].append(prev_links)

    return response


@current_app.route("/search", methods=["GET"])
@oauth2(required=False, throw_exception=False)
def stac_search_get(roles=None):
    """Search STAC items with simple filtering."""
    items = get_collection_items(**request.args, roles=roles)

    features = make_geojson(items.items, assets_kwargs=request.assets_kwargs)

    response = {
        "type": "FeatureCollection",
        "links": [],
        "context": {
            "matched": items.total,
            "returned": len(items.items),
        },
        "features": features,
    }

    args = request.args.copy()

    if items.has_next:

        args["page"] = items.next_num

        response["links"].append(
            {
                "href": f"{BDC_STAC_BASE_URL}/search{f'?{url_encode(args)}' if len(args) > 0 else ''}",
                "rel": "next",
            }
        )

    if items.has_prev:

        args["page"] = items.prev_num

        response["links"].append(
            {
                "href": f"{BDC_STAC_BASE_URL}/search{f'?{url_encode(args)}' if len(args) > 0 else ''}",
                "rel": "prev",
            }
        )

    return response


@current_app.errorhandler(Exception)
def handle_exception(err):
    """Handle exceptions."""
    if isinstance(err, HTTPException):
        return {"code": err.code, "description": err.description}, err.code

    current_app.logger.exception(err)

    return {"code": InternalServerError.code, "description": InternalServerError.description}, InternalServerError.code
