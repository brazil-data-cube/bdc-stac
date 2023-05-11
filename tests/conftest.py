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
"""Define the configuration for pytest and fixtures."""

import json
import os

import shapely
from bdc_catalog.models import Collection, GridRefSys, Item, Tile, db
from bdc_catalog.utils import create_collection, create_item, geom_to_wkb
from pytest import fixture

from bdc_stac import create_app


@fixture()
def load_fixture():
    """Initialize fixtures for STAC testing."""
    _setup_db()
    yield


@fixture(scope="class")
def client():
    """Retrieve Flask Test Client for STAC."""
    app = create_app()
    with app.test_client() as client:
        yield client


def _setup_db():
    app = create_app()

    with app.app_context():
        _setup_grid()
        _setup_initial_data()


def _setup_grid():
    grid_name = "BDC_SM_V2"
    tile = "020020"
    grs = GridRefSys.query().filter(GridRefSys.name == grid_name).first()
    if grs is None:
        geom = shapely.geometry.box(4736000, 9736000, 4841600, 9841600)
        features = [dict(id=1, tile=tile, geom=geom_to_wkb(geom, srid=100001))]
        grs = GridRefSys.create_geometry_table(table_name=grid_name, features=features, srid=100001, schema="bdc")

        db.session.add(grs)
        db.session.commit()

        geom_table = grs.geom_table
        for row in db.session.query(geom_table.c.tile).all():
            tile = Tile()
            tile.name = row.tile
            tile.grs = grs
            db.session.add(tile)
        db.session.commit()


def _setup_collection(data) -> Collection:
    items = data.pop("items", [])
    collection, _ = create_collection(**data)
    item_map = [i.name for i in db.session.query(Item.name).filter(Item.collection_id == collection.id).all()]

    tile_map = {}
    grid = GridRefSys.query().filter(GridRefSys.id == collection.grid_ref_sys_id).first()
    if grid:
        tile_map = {tile.name: tile.id for tile in Tile.query().filter(Tile.grid_ref_sys_id == grid.id).all()}

    for item in items:
        name = item.get("name")
        if name not in item_map:
            bbox = item.get("bbox")
            footprint = item.get("footprint")
            if bbox:
                item["bbox"] = shapely.geometry.shape(bbox)
                item["footprint"] = shapely.geometry.shape(footprint)
            tile_id = tile_map.get(item.get("tile_id"))
            item["tile_id"] = tile_id
            _ = create_item(collection_id=collection.id, **item)

    return collection


def _setup_initial_data():
    def _read(filename):
        with open(filename) as fd:
            data = json.load(fd)
        return data

    fixture_dir = "tests/fixtures"
    json_files = {filename: _read(os.path.join(fixture_dir, filename)) for filename in os.listdir(fixture_dir)}

    collection_v1 = _setup_collection(json_files["S2-16D-1.json"])
    collection_v2 = _setup_collection(json_files["S2-16D-2.json"])

    with db.session.begin_nested():
        collection_v1.version_successor = collection_v2.id
        collection_v2.version_predecessor = collection_v1.id

    db.session.commit()
