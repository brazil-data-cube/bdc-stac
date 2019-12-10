import os
import json
from copy import deepcopy
from collections import OrderedDict
from datetime import datetime
from sqlalchemy import create_engine, func, cast, select, text, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSONB
from geoalchemy2.functions import GenericFunction
from bdc_db.models import Collection, CollectionItem, Tile, Band, TemporalCompositionSchema, GrsSchema, Asset

import stac

connection = 'postgres://{}:{}@{}/{}'.format(os.environ.get('DB_USER'),
                                             os.environ.get('DB_PASS'),
                                             os.environ.get('DB_HOST'),
                                             os.environ.get('DB_NAME'))
db_engine = create_engine(connection, echo=True)

Session = sessionmaker(bind=db_engine)
session = Session()


class ST_Extent(GenericFunction):
    name = 'ST_Extent'
    type = None


def get_collection_items(collection_id=None, item_id=None, bbox=None, time=None, type=None, ids=None, bands=None,
                         collections=None):
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
               func.ST_AsGeoJson(Tile.geom_wgs84).label('geom'), assets.c.asset]
    where = [Collection.id == CollectionItem.collection_id, CollectionItem.tile_id == Tile.id,
             assets.c.item_id == CollectionItem.id]

    if ids is not None:
        where += [CollectionItem.id.in_(ids)]
    elif item_id is not None:
        where += [CollectionItem.id.like(item_id)]
    else:
        if collections is not None:
            where += [Collection.id.in_(collections)]
        elif collection_id is not None:
            where += [Collection.id.like(collection_id)]
        if bbox is not None:
            try:
                bbox = bbox.split(',')
                for x in bbox:
                    float(x)
                where += [func.ST_Intersects(
                    func.ST_MakeEnvelope(bbox[0], bbox[1], bbox[2], bbox[3], func.ST_SRID(Tile.geom_wgs84)),
                    Tile.geom_wgs84)]
            except:
                raise (InvalidBoundingBoxError())

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

    sql = session.query(*columns).filter(*where).group_by(*group_by).order_by(
        CollectionItem.composite_start.desc())
    result = sql.all()
    return result


def get_collection(collection_id):
    is_cube = session.query(Collection.is_cube).filter(Collection.id == collection_id).one().is_cube
    columns = [GrsSchema.id.label('grs_schema'),
               ST_Extent(Tile.geom_wgs84).label('bbox'),
               func.min(CollectionItem.composite_start).label('start'),
               func.max(CollectionItem.composite_end).label('end')]
    where = [Collection.id == CollectionItem.collection_id,
             CollectionItem.tile_id == Tile.id,
             Collection.grs_schema_id == GrsSchema.id,
             Collection.id == collection_id]
    group_by = [GrsSchema.id]

    if is_cube:
        columns += [TemporalCompositionSchema.temporal_schema.label('temporal_schema'),
                    TemporalCompositionSchema.temporal_composite_t.label('temporal_composite_t'),
                    TemporalCompositionSchema.temporal_composite_unit.label('temporal_composite_unit')]
        where += [Collection.temporal_composition_schema_id == TemporalCompositionSchema.id]

        group_by += [TemporalCompositionSchema.temporal_schema,
                     TemporalCompositionSchema.temporal_composite_t,
                     TemporalCompositionSchema.temporal_composite_unit]
    result = session.query(*columns) \
        .filter(*where).group_by(*group_by).one()
    bbox = result.bbox[result.bbox.find("(") + 1:result.bbox.find(")")].replace(' ', ',')

    collection = {}
    collection['id'] = collection_id
    start = result.start.isoformat()
    end = result.end.isoformat()

    collection["stac_version"] = os.getenv("API_VERSION")
    collection["description"] = ""

    collection["license"] = ""
    collection["properties"] = {}
    collection["extent"] = {"spatial": [float(coord) for coord in bbox.split(',')], "temporal": [start, end]}
    collection["properties"] = OrderedDict()

    tiles = session.query(CollectionItem.tile_id).filter(CollectionItem.collection_id == collection_id) \
        .group_by(CollectionItem.tile_id).all()
    collection
    collection["properties"]["bdc:tiles"] = [t.tile_id for t in tiles]

    bands = session.query(Band.common_name).filter(Band.collection_id == collection_id).all()

    collection["properties"]["bdc:bands"] = [b.common_name for b in bands]
    collection["properties"]["bdc:cube"] = is_cube

    if is_cube:
        collection["properties"]["bdc:tschema"] = result.temporal_schema
        collection["properties"]["bdc:tstep"] = result.temporal_composite_t
        collection["properties"]["bdc:tunit"] = result.temporal_composite_unit

    collection["properties"]["bdc:wrs"] = result.grs_schema

    return collection


def get_collections():
    collections = session.query(Collection.id).all()
    return collections


def make_geojson(items, links, page=1, limit=10, bands=None):
    features = []

    gjson = OrderedDict()
    gjson['type'] = 'FeatureCollection'

    if len(items) == 0:
        gjson['features'] = features
        return gjson

    p = (page - 1) * limit + limit
    min, max = (page - 1) * limit, \
               len(items) if p > len(items) else p

    for i in items[min:max]:
        feature = OrderedDict()

        feature['type'] = 'Feature'
        feature['id'] = i.item
        feature['collection'] = i.collection_id

        feature['geometry'] = json.loads(i.geom)
        feature['bbox'] = bbox(feature['geometry']['coordinates'])

        properties = OrderedDict()

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

    if len(features) == 1:
        return features[0]

    # TODO rever estratégia de page, limit
    gjson['features'] = features

    return gjson


def do_query(sql):
    connection = 'postgres://{}:{}@{}/{}'.format(os.environ.get('DB_USER'),
                                                 os.environ.get('DB_PASS'),
                                                 os.environ.get('DB_HOST'),
                                                 os.environ.get('DB_NAME'))
    engine = create_engine(connection)
    result = engine.execute(sql)
    result = result.fetchall()
    engine.dispose()
    result = [dict(row) for row in result]
    if len(result) > 0:
        return result
    else:
        return None


def bbox(coord_list):
    box = []
    for i in (0, 1):
        res = sorted(coord_list[0], key=lambda x: x[i])
        box.append((res[0][i], res[-1][i]))
    ret = [box[0][0], box[1][0], box[0][1], box[1][1]]
    return ret


class InvalidBoundingBoxError(Exception):
    pass
