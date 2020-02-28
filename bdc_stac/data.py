import json
import os
import warnings
from copy import deepcopy
from datetime import datetime

from bdc_db.models import (Asset, Band, Collection, CollectionItem, GrsSchema,
                           TemporalCompositionSchema, Tile)
from geoalchemy2.functions import GenericFunction
from sqlalchemy import cast, create_engine, exc, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import sessionmaker

with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=exc.SAWarning)

connection = 'postgresql://{}:{}@{}/{}'.format(os.environ.get('DB_USER'),
                                             os.environ.get('DB_PASS'),
                                             os.environ.get('DB_HOST'),
                                             os.environ.get('DB_NAME'))

db_engine = create_engine(connection)

Session = sessionmaker(bind=db_engine)
session = Session()


class ST_Extent(GenericFunction):
    name = 'ST_Extent'
    type = None


def get_collection_items(collection_id=None, item_id=None, bbox=None, time=None, ids=None, collections=None,
                         cubes=None, intersects=None, page=1, limit=10, **kwargs):
    x = session.query(CollectionItem.id.label('item_id'), Band.common_name.label('band'),
                      func.json_build_object('href', func.concat(os.getenv('FILE_ROOT'), Asset.url)).label('url')). \
        filter(Asset.collection_item_id == CollectionItem.id, Asset.band_id == Band.id).subquery('a')

    assets = session.query(x.c.item_id, cast(func.json_object_agg(x.c.band, x.c.url), JSONB).op('||')(
        cast(func.json_build_object('thumbnail', func.json_build_object('href', func.concat(os.getenv('FILE_ROOT'),
                                                                                            CollectionItem.quicklook))),
             JSONB)).label('asset')).filter(CollectionItem.id == x.c.item_id).group_by(x.c.item_id,
                                                                                       CollectionItem.quicklook) \
        .subquery('b')

    columns = [Collection.id.label('collection_id'), CollectionItem.id.label('item'),
               CollectionItem.composite_start.label('start'),
               CollectionItem.composite_end.label('end'), Tile.id.label('tile'),
               func.ST_AsGeoJSON(Tile.geom_wgs84).label('geom'), assets.c.asset]
    where = [Collection.id == CollectionItem.collection_id, CollectionItem.tile_id == Tile.id,
             assets.c.item_id == CollectionItem.id, CollectionItem.grs_schema_id == Tile.grs_schema_id]

    if ids is not None:
        where += [CollectionItem.id.in_(ids.split(','))]
    elif item_id is not None:
        where += [CollectionItem.id.like(item_id)]
    else:
        if cubes is not None:
            where+= [Collection.is_cube.is_(cubes=='true')]
        if collections is not None:
            where += [Collection.id.in_(collections.split(','))]
        elif collection_id is not None:
            where += [Collection.id.like(collection_id)]

        if intersects is not None:
            where += [func.ST_Intersects(func.ST_GeomFromGeoJSON(str(intersects['geometry'])), Tile.geom_wgs84)]

        if bbox is not None:
            try:
                split_bbox = bbox.split(',')
                for x in split_bbox:
                    float(x)
                where += [func.ST_Intersects(
                    func.ST_MakeEnvelope(split_bbox[0], split_bbox[1], split_bbox[2], split_bbox[3], func.ST_SRID(Tile.geom_wgs84)),
                    Tile.geom_wgs84)]
            except:
                raise (InvalidBoundingBoxError(f"'{bbox}' is not a valid bbox.'"))

        if time is not None:
            if "/" in time:
                time_start, end = time.split("/")
                time_end = datetime.fromisoformat(end)
                where += [CollectionItem.composite_end <= time_end]
            else:
                time_start = datetime.fromisoformat(time)
            where += [CollectionItem.composite_start >= time_start]
    group_by = [Collection.id, CollectionItem.id, CollectionItem.composite_start, CollectionItem.composite_end,
                Tile.id, Tile.geom_wgs84, assets.c.asset]

    query = session.query(*columns).filter(*where).group_by(*group_by).order_by(
        CollectionItem.composite_start.desc())

    if limit:
        query = query.limit(int(limit))
    if page:
        query = query.offset((int(page) * int(limit)) - int(limit))

    result = query.all()
    return result

def get_collection_bands(collection_id):
    bands = session.query(Band).filter(Band.collection_id == collection_id).all()
    bands_json = dict()

    for b in bands:
        bands_json[b.common_name] = {k: v for k, v in b.__dict__.items() if
                                     k != 'common_name' and not k.startswith('_')}
        bands_json[b.common_name].pop("id")
        bands_json[b.common_name].pop("collection_id")

    return bands_json

def get_collection_tiles(collection_id):
    tiles = session.query(CollectionItem.tile_id).filter(CollectionItem.collection_id == collection_id) \
        .group_by(CollectionItem.tile_id).all()

    return [t.tile_id for t in tiles]

def collection_is_cube(collection_id):
    return session.query(Collection.is_cube).filter(Collection.id == collection_id).one().is_cube

def get_collection(collection_id):
    columns = [CollectionItem.grs_schema_id.label('grs_schema'),
               ST_Extent(Tile.geom_wgs84).label('bbox'),
               func.min(CollectionItem.composite_start).label('start'),
               func.max(CollectionItem.composite_end).label('end')]
    where = [Collection.id == CollectionItem.collection_id,
             CollectionItem.tile_id == Tile.id,
             CollectionItem.grs_schema_id == Tile.grs_schema_id,
             Collection.id == collection_id]
    group_by = [CollectionItem.grs_schema_id]

    is_cube = collection_is_cube(collection_id)

    if is_cube:
        columns += [TemporalCompositionSchema.temporal_schema.label('temporal_schema'),
                    TemporalCompositionSchema.temporal_composite_t.label('temporal_composite_t'),
                    TemporalCompositionSchema.temporal_composite_unit.label('temporal_composite_unit')]
        where += [Collection.temporal_composition_schema_id == TemporalCompositionSchema.id]

        group_by += [TemporalCompositionSchema.temporal_schema,
                     TemporalCompositionSchema.temporal_composite_t,
                     TemporalCompositionSchema.temporal_composite_unit]
    result = session.query(*columns) \
        .filter(*where).group_by(*group_by).first()

    bbox = list()
    if result.bbox:
        bbox = result.bbox[result.bbox.find("(") + 1:result.bbox.find(")")].replace(' ', ',')
        bbox = [float(coord) for coord in bbox.split(',')]

    collection = dict()
    collection['id'] = collection_id

    start, end = None, None

    if result.start:
        start = result.start.isoformat()
        if result.end:
            end = result.end.isoformat()

    bands = get_collection_bands(collection_id)
    tiles = get_collection_tiles(collection_id)

    collection["stac_version"] = os.getenv("API_VERSION")


    collection["description"] = f"{collection_id} collection with {', '.join([k for k in bands.keys()])} bands"

    collection["license"] = ""
    collection["properties"] = dict()
    collection["extent"] = {"spatial": bbox, "temporal": [start, end]}
    collection["properties"] = dict()

    collection["properties"]["bdc:tiles"] = tiles

    collection["properties"]["bdc:bands"] = bands
    collection["properties"]["bdc:cube"] = is_cube

    if is_cube:
        temporal_schema = dict()
        temporal_schema['schema'] = result.temporal_schema
        temporal_schema['step'] = result.temporal_composite_t
        temporal_schema['unit'] = result.temporal_composite_unit
        collection["properties"]["bdc:temporal_composition"] = temporal_schema

    collection["properties"]["bdc:wrs"] = result.grs_schema

    return collection


def get_collections():
    collections = session.query(Collection.id).filter(CollectionItem.collection_id == Collection.id)\
	        .group_by(Collection.id).all()
    return collections


def make_geojson(items, links):
    features = list()

    for i in items:
        feature = dict()

        feature['type'] = 'Feature'
        feature['id'] = i.item
        feature['collection'] = i.collection_id
        feature['stac_version'] = os.getenv("API_VERSION")

        feature['geometry'] = json.loads(i.geom)
        feature['bbox'] = get_bbox(feature['geometry']['coordinates'])

        properties = dict()

        start = datetime.fromisoformat(str(i.start)).isoformat()
        properties['bdc:tile'] = i.tile
        properties['datetime'] = f"{start}"
        feature['properties'] = properties

        feature['assets'] = i.asset
        feature['links'] = deepcopy(links)
        feature['links'][0]['href'] += i.collection_id + "/items/" + i.item
        feature['links'][1]['href'] += i.collection_id
        feature['links'][2]['href'] += i.collection_id

        features.append(feature)

    return features


def get_bbox(coord_list):
    box = list()
    for i in (0, 1):
        res = sorted(coord_list[0], key=lambda x: x[i])
        box.append((res[0][i], res[-1][i]))
    ret = [box[0][0], box[1][0], box[0][1], box[1][1]]
    return ret


class InvalidBoundingBoxError(Exception):
    def __init__(self, description):
        self.description = description

    def __str__(self):
        return str(self.description)
