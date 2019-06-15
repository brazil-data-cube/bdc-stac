from flask import Flask, jsonify, request
from flasgger import Swagger, swag_from
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

import data

app = Flask(__name__)

app.config["SWAGGER"] = {
    "openapi": "3.0.1"
}

swagger = Swagger(app, template_file="./openapi/STAC.yaml")


@app.route("/")
def index():
    return "Hello World"


@app.route("/conformance")
def conformance():
    return "Hello World"


@app.route("/collections")
def collections():
    return "Hello World"


@app.route("/collections/<collection_id>")
def collections_id(collection_id):
    return "Hello World"


@app.route("/collections/<collection_id>/items")
def items(collection_id):
    return "Hello World"


@app.route("/collections/<collection_id>/items/<item_id>")
def items_id(collection_id, item_id):
    return "Hello World"


@app.route("/stac")
def stac():
    datacubes = data.get_datacubes()
    catalog = dict()
    catalog["description"] = "Brazil Data Cubes Catalog"
    catalog["id"] = "bdc"
    catalog["stac_version"] = "0.7"
    links = list()
    links.append({"href": request.url, "rel": "self"})

    for datacube in datacubes:
        links.append({"href": f"{request.url_root}collections/{datacube['datacube']}", "rel": "child"})

    catalog["links"] = links

    return jsonify(catalog)


@app.route("/stac/search")
def stac_search():
    return "Hello"


if __name__ == "__main__":
    app.run(debug=True)
