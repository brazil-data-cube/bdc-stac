"""Data module."""
import json
import warnings
from copy import deepcopy
from datetime import datetime

from bdc_catalog.models import (Band, Collection, CompositeFunction, Item, GridRefSys, Tile, Quicklook, db)
from geoalchemy2.functions import GenericFunction
from sqlalchemy import cast, create_engine, exc, func, or_, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import sessionmaker

from .config import (BDC_STAC_FILE_ROOT, BDC_STAC_API_VERSION,
                     BDC_STAC_MAX_LIMIT)

with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=exc.SAWarning)

session = db.create_scoped_session({'autocommit': True})


class ST_Extent(GenericFunction):
    """Postgis ST_Extent function."""

    name = 'ST_Extent'
    type = None


def get_collection_items(collection_id=None, roles=[], item_id=None, bbox=None, time=None, ids=None, collections=None,
                         cubes=None, intersects=None, page=1, limit=10, query=None, **kwargs):
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
    columns = [Collection.name.label('collection'),
               Item.name.label('item'),
               Item.start_date.label('start'),
               Item.end_date.label('end'),
               Item.assets,
               func.ST_AsGeoJSON(Item.geom).label('geom'),
               func.Box2D(Item.geom).label('bbox'),
               Tile.name.label('tile')]

    where = [Collection.id == Item.collection_id,
              Item.tile_id == Tile.id,
              or_(
                Collection.is_public.is_(True),
                Collection.id.in_([int(r.split(':')[0]) for r in roles])
             )]

    if ids is not None:
        where += [Item.id.in_(ids.split(','))]
    elif item_id is not None:
        where += [Item.id.like(item_id)]
    else:
        if collections is not None:
            where += [Collection.name.in_(collections.split(','))]
        elif collection_id is not None:
            where += [Collection.name.like(collection_id)]

        if intersects is not None:
            where += [func.ST_Intersects(func.ST_GeomFromGeoJSON(
                str(intersects)), Item.geom)]

        if query:
           filters =  create_query_filter(query)
           if filters:
               where += filters

        if bbox is not None:
            try:
                split_bbox = [float(x) for x in bbox.split(',')]

                where += [func.ST_Intersects(func.ST_MakeEnvelope(split_bbox[0],
                                                                  split_bbox[1],
                                                                  split_bbox[2],
                                                                  split_bbox[3],
                                                                  func.ST_SRID(Item.geom)),
                                             Item.geom)]
            except:
                raise (InvalidBoundingBoxError(
                    f"'{bbox}' is not a valid bbox.'"))

        if time is not None:
            if "/" in time:
                time_start, time_end = time.split("/")
                time_end = datetime.fromisoformat(time_end)
                where += [or_(Item.end_date <= time_end,
                              Item.start_date <= time_end)]
            else:
                time_start = datetime.fromisoformat(time)
            where += [or_(Item.start_date >= time_start,
                        Item.end_date >= time_start)]


    query = session.query(*columns).filter(*where).order_by(Item.start_date.desc())

    result = query.paginate(page=int(page),
                            per_page=int(limit),
                            error_out=False,
                            max_per_page=int(BDC_STAC_MAX_LIMIT))

    return result


def get_collection_bands(collection_id):
    """Retrive a dict of bands for a given collection.

    :param collection_id: collection identifier
    :type collection_id: str
    :return: dict of bands for the collection
    :rtype: dict
    """
    bands = session.query(Band.name, Band.common_name, Band.description,
                          cast(Band.min, Float).label('min'), cast(Band.max, Float).label('max'),
                          cast(Band.nodata, Float).label('nodata'), cast(Band.scale, Float).label('scale'),
                          cast(Band.resolution_x, Float).label('resolution_x'), cast(Band.resolution_y, Float).label('resolution_y'),
                               Band.data_type).filter(Band.collection_id == collection_id).all()
    bands_json = dict()

    for b in bands:
        bands_json[b.common_name] = {k: v for k, v in b._asdict().items() if
                                     k != 'common_name' and not k.startswith('_')}

    return bands_json


def get_collection_tiles(collection_id):
    """Retrive a list of tiles for a given collection.

    :param collection_id: collection identifier
    :type collection_id: str
    :return: list of tiles for the collection
    :rtype: list
    """
    tiles = session.query(Tile.name) \
                   .filter(Item.collection_id == collection_id,
                           Item.tile_id == Tile.id).group_by(Tile.name).all()

    return [t.name for t in tiles]

def get_collection_crs(collection_id):
    """Retrive the CRS for a given collection.

    :param collection_id: collection identifier
    :type collection_id: str
    :return: CRS for the collection
    :rtype: list
    """
    crs = session.execute("SELECT spatial_ref_sys.proj4text as proj "
                          "FROM grid_ref_sys, pg_class, geometry_columns, spatial_ref_sys, collections "
                          "WHERE grid_ref_sys.table_id = pg_class.oid "
                          "AND geometry_columns.f_table_name = relname "
                          "AND geometry_columns.f_table_schema = relnamespace::regnamespace::text "
                          "AND spatial_ref_sys.srid = geometry_columns.srid "
                          "AND collections.grid_ref_sys_id = grid_ref_sys.id "
                          "AND collections.id = :collection_id", {"collection_id": collection_id}).first()

    return crs["proj"]

def get_collection_timeline(collection_id):
    """Retrive a list of dates for a given collection.

    :param collection_id: collection identifier
    :type collection_id: str
    :return: list of dates for the collection
    :rtype: list
    """
    timeline = session.query(Item.start_date).filter(Item.collection_id == collection_id) \
        .group_by(Item.start_date).order_by(Item.start_date.asc()).all()

    return [datetime.fromisoformat(str(t.start_date)).strftime("%Y-%m-%d") for t in timeline]

def get_collection_extent(collection_id):
    """Retrive the extent as a BBOX for a given collection.

        :param collection_id: collection identifier
        :type collection_id: str
        :return: list of coordinates for the collection extent
        :rtype: lis
    """
    extent = session.query(func.ST_Extent(Item.geom).label('bbox'))\
                    .filter(Collection.id == Item.collection_id,
                            Collection.id == collection_id).first()

    bbox = list()
    if extent.bbox:
        bbox = extent.bbox[extent.bbox.find(
            "(") + 1:extent.bbox.find(")")].replace(' ', ',')
        bbox = [float(coord) for coord in bbox.split(',')]
    return bbox

def get_collection_quicklook(collection_id):
    """Retrive a list of bands used to create the quicklooks for a given collection.

        :param collection_id: collection identifier
        :type collection_id: str
        :return: list of bands
        :rtype: lis
    """
    quicklook_bands = session.execute("SELECT  array[r.name, g.name, b.name] as quicklooks "
                                      "FROM bdc.quicklook q "
                                      "INNER JOIN bdc.bands r ON q.red = r.id "
                                      "INNER JOIN bdc.bands g ON q.green = g.id "
                                      "INNER JOIN bdc.bands b ON q.blue = b.id "
                                      "INNER JOIN bdc.collections c ON q.collection_id = c.id "
                                      "WHERE c.id = :collection_id", {"collection_id":collection_id}).fetchone()
    return quicklook_bands["quicklooks"]

def get_collection(collection_id, roles=[]):
    """Retrieve information of a given collection.

    :param collection_id: collection identifier
    :type collection_id: str
    :return: collection metadata
    :rtype: dict
    """
    columns = [ST_Extent(Item.geom).label('bbox'),
               Collection.id,
               Collection.is_public,
               Collection.start_date.label('start'),
               Collection.end_date.label('end'),
               Collection.description,
               Collection.name,
               Collection.version,
               Collection.temporal_composition_schema,
               CompositeFunction.name.label('composite_function'),
               GridRefSys.name.label('grid_ref_sys')]

    where = [Collection.id == Item.collection_id,
             Collection.name == collection_id,
             Collection.grid_ref_sys_id == GridRefSys.id,
             or_(
                Collection.is_public.is_(True),
                Collection.id.in_([int(r.split(':')[0]) for r in roles])
             )]

    group_by = [Collection.id,
                Collection.start_date,
                Collection.end_date,
                Collection.description,
                Collection.name,
                Collection.version,
                Collection.temporal_composition_schema,
                CompositeFunction.name,
                GridRefSys.name]

    result = session.query(*columns).outerjoin(Collection, Collection.composite_function_id == CompositeFunction.id) \
        .filter(*where).group_by(*group_by).first_or_404()

    collection = dict()
    collection['id'] = collection_id

    collection["stac_version"] = BDC_STAC_API_VERSION
    collection["description"] = result.description
    collection["license"] = ""

    collection["properties"] = dict()

    bbox = get_collection_extent(result.id)

    start, end = None, None

    if result.start:
        start = result.start.strftime("%Y-%m-%d")
        if result.end:
            end = result.end.strftime("%Y-%m-%d")

    collection["extent"] = {"spatial": {"bbox": [bbox]},
                            "temporal": {"interval": [[start, end]]}}

    quicklooks = get_collection_quicklook(result.id)
    if quicklooks is not None:
        collection["properties"]["bdc:bands_quicklook"] = quicklooks

    bands = get_collection_bands(result.id)
    collection["properties"]["bdc:bands"] = bands

    collection["properties"]["bdc:crs"] = get_collection_crs(result.id)
    collection["properties"]["bdc:wrs"] = result.grid_ref_sys

    if result.temporal_composition_schema:
        collection["properties"]["bdc:temporal_composition"] = result.temporal_composition_schema
        collection["properties"]["bdc:timeline"] = get_collection_timeline(result.id)
        collection["properties"]["bdc:composite_function"] = result.composite_function
        collection["properties"]["bdc:tiles"] = get_collection_tiles(result.id)

    return collection


def get_collections(roles=[]):
    """Retrive all available collections.

    :return: a list of available collections
    :rtype: list
    """
    collections = session.query(Collection.name, Collection.id).filter(or_(
        Collection.is_public.is_(True),
        Collection.id.in_([int(r.split(':')[0]) for r in roles])
    )).all()
    return collections


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
        feature['collection'] = i.collection
        feature['stac_version'] = BDC_STAC_API_VERSION

        feature['geometry'] = json.loads(i.geom)

        bbox = list()
        if i.bbox:
            bbox = i.bbox[i.bbox.find(
                "(") + 1:i.bbox.find(")")].replace(' ', ',')
            bbox = [float(coord) for coord in bbox.split(',')]
        feature['bbox'] = bbox

        properties = dict()

        start = datetime.fromisoformat(str(i.start)).strftime("%Y-%m-%d")
        properties['bdc:tile'] = i.tile
        properties['datetime'] = f"{start}"
        feature['properties'] = properties

        for key, value in i.assets.items():
            value['href'] = BDC_STAC_FILE_ROOT + value['href']
        feature['assets'] = i.assets

        feature['links'] = deepcopy(links)
        feature['links'][0]['href'] += i.collection + "/items/" + i.item
        feature['links'][1]['href'] += i.collection
        feature['links'][2]['href'] += i.collection

        features.append(feature)

    return features

def create_query_filter(query):
    """Create STAC query filter for SQLAlchemy
    Notes:
        Queryable properties must be mapped in this functions.
    """

    mapping = {
        'eq': '__eq__',
        'neq': '__ne__',
        'lt': '__lt__',
        'lte': '__le__',
        'gt': '__gt__',
        'gte': '__ge__',
        'startsWith': 'startswith',
        'endsWith': 'endswith',
        'contains':'contains',
        'in': 'in_',
    }

    bdc_properties = {
        "bdc:tiles": Tile.name
    }

    filters = []

    for column, _filters in query.items():
        for op, value in _filters.items():
            f = getattr(bdc_properties[column], mapping[op])(value)
            filters.append(f)

    return filters if len(filters) > 0 else None

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
