"""Data module."""
import json
import os
import warnings
from copy import deepcopy
from datetime import datetime

from bdc_db.models import (Asset, Band, Collection, CollectionItem,
                           CompositeFunctionSchema, GrsSchema,
                           TemporalCompositionSchema, Tile, db)
from geoalchemy2.functions import GenericFunction
from sqlalchemy import cast, create_engine, exc, func, or_
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects import postgresql

with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=exc.SAWarning)

session = db.create_scoped_session({'autocommit': True})


class ST_Extent(GenericFunction):
    """Postgis ST_Extent function."""

    name = 'ST_Extent'
    type = None


def get_collection_items(collection_id=None, item_id=None, bbox=None, time=None, ids=None, collections=None,
                         cubes=None, intersects=None, page=1, limit=10, **kwargs):
    """Retrieve a list of collection items based on filters.

    :param collection_id: Single Collection ID to include in the search for items.
                          Only Items in one of the provided Collection will be searched, defaults to None
    :type collection_id: str, optional
    :param item_id: item identifier, defaults to None
    :type item_id: str, optional
    :param bbox: bounding box for intersection [west, north, east, south], defaults to None
    :type bbox: list, optional
    :param time: Single date+time, or a range ('/' seperator), formatted to RFC 3339, section 5.6, defaults to None
    :type time: str, optional
    :param ids: Array of Item ids to return. All other filter parameters that further restrict the
                number of search results are ignored, defaults to None
    :type ids: list, optional
    :param collections: Array of Collection IDs to include in the search for items.
                        Only Items in one of the provided Collections will be searched, defaults to None
    :type collections: list, optional
    :param cubes: Bool indicating if only cubes should be returned, defaults to None
    :type cubes: bool, optional
    :param intersects: Searches items by performing intersection between their geometry and provided GeoJSON geometry.
                       All GeoJSON geometry types must be supported., defaults to None
    :type intersects: dict, optional
    :param page: The page offset of results, defaults to 1
    :type page: int, optional
    :param limit: The maximum number of results to return (page size), defaults to 10
    :type limit: int, optional
    :return: list of collectio items
    :rtype: list
    """

    columns = [Collection.id.label('collection_id'), CollectionItem.id.label('item'),
               CollectionItem.composite_start.label('start'),
               CollectionItem.composite_end.label(
                   'end'), Tile.id.label('tile'),
               func.ST_AsGeoJSON(Tile.geom_wgs84).label(
                   'geom'), CollectionItem.quicklook,
               func.Box2D(Tile.geom_wgs84).label('bbox')]
    where = [Collection.id == CollectionItem.collection_id, CollectionItem.tile_id == Tile.id,
             CollectionItem.grs_schema_id == Tile.grs_schema_id]

    if ids is not None:
        where += [CollectionItem.id.in_(ids.split(','))]
    elif item_id is not None:
        where += [CollectionItem.id.like(item_id)]
    else:
        if cubes is not None:
            where += [Collection.is_cube.is_(cubes == 'true')]
        if collections is not None:
            where += [Collection.id.in_(collections.split(','))]
        elif collection_id is not None:
            where += [Collection.id.like(collection_id)]

        if intersects is not None:
            where += [func.ST_Intersects(func.ST_GeomFromGeoJSON(
                str(intersects['geometry'])), Tile.geom_wgs84)]

        if bbox is not None:
            try:
                split_bbox = bbox.split(',')
                for x in split_bbox:
                    float(x)
                where += [func.ST_Intersects(
                    func.ST_MakeEnvelope(
                        split_bbox[0], split_bbox[1], split_bbox[2], split_bbox[3], func.ST_SRID(Tile.geom_wgs84)),
                    Tile.geom_wgs84)]
            except:
                raise (InvalidBoundingBoxError(
                    f"'{bbox}' is not a valid bbox.'"))

        if time is not None:
            if "/" in time:
                time_start, end = time.split("/")
                time_end = datetime.fromisoformat(end)
                where += [or_(CollectionItem.composite_end <= time_end,
                              CollectionItem.composite_start <= time_end)]
            else:
                time_start = datetime.fromisoformat(time)
            where += [or_(CollectionItem.composite_start >= time_start,
                          CollectionItem.composite_end >= time_start)]
    group_by = [Collection.id, CollectionItem.id, CollectionItem.composite_start, CollectionItem.composite_end,
                Tile.id, Tile.geom_wgs84, CollectionItem.quicklook]

    query = session.query(*columns).filter(*where).group_by(*group_by).order_by(
        CollectionItem.composite_start.desc())

    result = query.paginate(page=int(page), per_page=int(
        limit), error_out=False, max_per_page=int(os.getenv('MAX_LIMIT', 100)))

    return result


def get_collection_bands(collection_id):
    """Retrive a dict of bands for a given collection.

    :param collection_id: collection identifier
    :type collection_id: str
    :return: dict of bands for the collection
    :rtype: dict
    """
    bands = session.query(Band).filter(
        Band.collection_id == collection_id).all()
    bands_json = dict()

    for b in bands:
        bands_json[b.common_name] = {k: v for k, v in b.__dict__.items() if
                                     k != 'common_name' and not k.startswith('_')}
        bands_json[b.common_name].pop("id")
        bands_json[b.common_name].pop("collection_id")

    return bands_json


def get_collection_tiles(collection_id):
    """Retrive a list of tiles for a given collection.

    :param collection_id: collection identifier
    :type collection_id: str
    :return: list of tiles for the collection
    :rtype: list
    """
    tiles = session.query(CollectionItem.tile_id).filter(CollectionItem.collection_id == collection_id) \
        .group_by(CollectionItem.tile_id).all()

    return [t.tile_id for t in tiles]


def collection_is_cube(collection_id):
    """Check if a collection is a cube.

    :param collection_id: collection identifier
    :type collection_id: str
    :return: True if the given collection is a cube, False otherwise
    :rtype: bool
    """
    return session.query(Collection.is_cube).filter(Collection.id == collection_id).one().is_cube


def get_collection_timeline(collection_id):
    """Retrive a list of dates for a given collection.

    :param collection_id: collection identifier
    :type collection_id: str
    :return: list of dates for the collection
    :rtype: list
    """
    timeline = session.query(CollectionItem.composite_start).filter(CollectionItem.collection_id == collection_id) \
        .group_by(CollectionItem.composite_start).order_by(CollectionItem.composite_start.asc()).all()

    return [datetime.fromisoformat(str(t.composite_start)).strftime("%Y-%m-%d") for t in timeline]


def get_collection(collection_id):
    """Retrieve information of a given collection.

    :param collection_id: collection identifier
    :type collection_id: str
    :return: collection metadata
    :rtype: dict
    """
    columns = [CollectionItem.grs_schema_id.label('grs_schema'),
               ST_Extent(Tile.geom_wgs84).label('bbox'),
               func.min(CollectionItem.composite_start).label('start'),
               func.max(CollectionItem.composite_end).label('end'),
               Collection.bands_quicklook,
               Collection.description,
               GrsSchema.crs.label('crs'),
               CompositeFunctionSchema.id.label('composite_function')]
    where = [Collection.id == CollectionItem.collection_id,
             CollectionItem.tile_id == Tile.id,
             CollectionItem.grs_schema_id == Tile.grs_schema_id,
             Collection.id == collection_id,
             CompositeFunctionSchema.id == Collection.composite_function_schema_id,
             GrsSchema.id == Collection.grs_schema_id]
    group_by = [CollectionItem.grs_schema_id,
                Collection.bands_quicklook,
                Collection.description,
                GrsSchema.crs,
                CompositeFunctionSchema.id]

    is_cube = collection_is_cube(collection_id)

    if is_cube:
        columns += [TemporalCompositionSchema.temporal_schema.label('temporal_schema'),
                    TemporalCompositionSchema.temporal_composite_t.label(
                        'temporal_composite_t'),
                    TemporalCompositionSchema.temporal_composite_unit.label('temporal_composite_unit')]
        where += [Collection.temporal_composition_schema_id ==
                  TemporalCompositionSchema.id]

        group_by += [TemporalCompositionSchema.temporal_schema,
                     TemporalCompositionSchema.temporal_composite_t,
                     TemporalCompositionSchema.temporal_composite_unit]
    result = session.query(*columns) \
        .filter(*where).group_by(*group_by).first()

    bbox = list()
    if result.bbox:
        bbox = result.bbox[result.bbox.find(
            "(") + 1:result.bbox.find(")")].replace(' ', ',')
        bbox = [float(coord) for coord in bbox.split(',')]

    collection = dict()
    collection['id'] = collection_id

    start, end = None, None

    if result.start:
        start = result.start.strftime("%Y-%m-%d")
        if result.end:
            end = result.end.strftime("%Y-%m-%d")

    bands = get_collection_bands(collection_id)
    tiles = get_collection_tiles(collection_id)

    collection["stac_version"] = os.getenv("API_VERSION", "0.8.0")

    collection["description"] = result.description

    collection["license"] = ""
    collection["properties"] = dict()
    collection["extent"] = {"spatial": {"bbox": [bbox]},
                            "temporal": {"interval": [[start, end]]}}
    collection["properties"] = dict()

    collection["properties"]["bdc:tiles"] = tiles
    if result.bands_quicklook is not None:
        collection["properties"]["bdc:bands_quicklook"] = result.bands_quicklook.split(
            ",")
    collection["properties"]["bdc:bands"] = bands
    collection["properties"]["bdc:cube"] = is_cube
    collection["properties"]["bdc:crs"] = result.crs

    if is_cube:
        temporal_schema = dict()
        temporal_schema['schema'] = result.temporal_schema
        temporal_schema['step'] = result.temporal_composite_t
        temporal_schema['unit'] = result.temporal_composite_unit
        collection["properties"]["bdc:temporal_composition"] = temporal_schema
        collection["properties"]["bdc:timeline"] = get_collection_timeline(
            collection_id)
        collection["properties"]["bdc:composite_function"] = result.composite_function
    collection["properties"]["bdc:wrs"] = result.grs_schema

    return collection


def get_collections():
    """Retrive all available collections.

    :return: a list of available collections
    :rtype: list
    """
    collections = session.query(Collection.id).filter(CollectionItem.collection_id == Collection.id)\
        .group_by(Collection.id).all()
    return collections


def get_assets(item_id):
    """Retrive all assets for an item.

    :param item_id: collection item identifier
    :type item_id: str
    """
    assets = session.query(Asset.url, Band.common_name.label('band')).filter(
        Asset.collection_item_id == item_id, Asset.band_id == Band.id).group_by(Asset.url, Band.common_name).all()

    return assets

def make_geojson(items, links):
    """Generate a list of STAC Items from a list of collection items.

    :param items: collection items to be formated as GeoJSON Features
    :type items: list
    :param links: links for STAC navigation
    :type links: list
    :return: GeoJSON Features.
    :rtype: list
    """
    features = list()

    for i in items:
        feature = dict()

        feature['type'] = 'Feature'
        feature['id'] = i.item
        feature['collection'] = i.collection_id
        feature['stac_version'] = os.getenv("API_VERSION", "0.8.0")

        feature['geometry'] = json.loads(i.geom)

        bbox = list()
        if i.bbox:
            bbox = i.bbox[i.bbox.find(
                "(") + 1:i.bbox.find(")")].replace(' ', ',')
            bbox = [float(coord) for coord in bbox.split(',')]
        feature['bbox'] = bbox


        assets = get_assets(i.item)
        feature['assets'] = dict()
        asset_path = os.getenv('FILE_ROOT')
        feature['assets']['thumbnail'] = {'href': asset_path + i.quicklook}

        for a in assets:
            feature['assets'][a.band] = {'href': asset_path + a.url}

        properties = dict()
        start = datetime.fromisoformat(str(i.start)).strftime("%Y-%m-%d")
        properties['bdc:tile'] = i.tile
        properties['datetime'] = start
        feature['properties'] = properties

        feature['links'] = deepcopy(links)
        feature['links'][0]['href'] += i.collection_id + "/items/" + i.item
        feature['links'][1]['href'] += i.collection_id
        feature['links'][2]['href'] += i.collection_id

        features.append(feature)

    return features


class InvalidBoundingBoxError(Exception):
    """Exception for malformed bounding box."""

    def __init__(self, description):
        """Initialize exception with a description.

        :param description: exception description.
        :type description: str
        """
        self.description = description

    def __str__(self):
        """:return: str representation of the exception."""
        return str(self.description)
