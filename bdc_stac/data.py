import sqlalchemy
import os
import json
from collections import OrderedDict
from datetime import datetime
from copy import deepcopy


def get_collection_items(collection_id=None, item_id=None, bbox=None, time=None, type=None, ids=None, bands=None,
                         collections=None):
    sql = f"SELECT a.id as cube_collection, b.id as item, b.composite_start as start, b.composite_end as end, b.quicklook, " \
          f"c.id as tileid, ST_AsGeoJson(c.geom_wgs84) as geom, e.id as type, " \
          f"(SELECT json_build_object('thumbnail', json_build_object('href', concat('{os.getenv('FILE_ROOT')}', b.quicklook)))::jsonb ||" \
          f"(SELECT json_object_agg(x.band, x.url)" \
          f"FROM (SELECT y.common_name as band, json_build_object('href', concat('{os.getenv('FILE_ROOT')}', url)) as url " \
          f"FROM assets x, bands y " \
          f"WHERE cube_item = b.id and x.band = y.id) x)::jsonb) as assets " \
          f"FROM cube_collections a, cube_items b, tiles c, composite_functions e " \
          f"WHERE "

    where = list()
    where.append(f"a.id = b.cube_collection and b.tile = c.id and b.composite_function = e.id")

    if ids is not None:
        where.append(f"FIND_IN_SET(b.id, '{ids}')")
    elif item_id is not None:
        where.append(f"b.id LIKE '{item_id}'")
    else:
        if collections is not None:
            where.append(f"FIND_IN_SET(a.id, '{collections}')")
        elif collection_id is not None:
            where.append(f"a.id LIKE '{collection_id}'")
        if bbox is not None:
            try:
                bbox = bbox.split(',')
                for x in bbox:
                    float(x)

                where.append(
                    f"ST_Intersects(ST_MakeEnvelope({bbox[0]}, {bbox[1]}, {bbox[2]}, {bbox[3]}, ST_SRID(c.geom_wgs84)), c.geom_wgs84)")
            except:
                raise (InvalidBoundingBoxError())

        if time is not None:
            if "/" in time:
                time_start, end = time.split("/")
                time_end = datetime.fromisoformat(end)
                where.append(f"b.composite_end <= '{time_end}'")
            else:
                time_start = datetime.fromisoformat(time)
            where.append(f"b.composite_start >= '{time_start}'")
    if type is not None:
        where.append(f"`type` LIKE '{type}'")
    where.append(f"e.id != 'SCENE'")

    where = " AND ".join(where)
    group = f" GROUP BY a.id, b.id, b.composite_start, b.composite_end, b.quicklook, c.id, c.geom_wgs84, e.id " \
            f"ORDER BY b.composite_start DESC"

    sql += where + group
    items = do_query(sql)

    return items


def get_collection(collection_id):
    extent = do_query(f"select ST_EXTENT(d.geom_wgs84)as extent FROM cube_collections a, cube_items c, tiles d "
                      f"WHERE '{collection_id}' = a.id AND c.tile = d.id GROUP BY a.id;")[0]['extent']
    extent = extent[extent.find("(") + 1:extent.find(")")].replace(' ', ',')

    minmax_date = do_query(f"SELECT a.id as id, MIN(b.composite_start) as start, MAX(b.composite_end) as end "
                           f"FROM cube_collections a, cube_items b "
                           f"WHERE '{collection_id}' = a.id and a.id = b.cube_collection "
                           f"GROUP BY a.id;")[0]

    collection = {}
    collection['id'] = collection_id
    start = minmax_date['start'].isoformat()
    end = None if minmax_date['end'] is None else minmax_date['end'].isoformat()

    collection["stac_version"] = os.getenv("API_VERSION")
    collection["description"] = ""

    collection["license"] = None
    collection["properties"] = {}
    collection["extent"] = {"spatial": [float(x) for x in extent.split(',')], "time": [start, end]}
    collection["properties"] = OrderedDict()

    types = do_query(f"SELECT b.id FROM cube_collections a, composite_functions b "
                     f"WHERE '{collection_id}' = a.id and a.id = b.cube_collection")
    collection["properties"]["bdc:time_aggregations"] = [{"name": t['id'], "description": None} for t in types]

    tiles = do_query(f"SELECT a.id, c.tile "
                     f"FROM cube_collections a, cube_tiles b, cube_items c, tiles d "
                     f"WHERE '{collection_id}' = a.id and a.id = b.cube_collection and a.id = c.cube_collection "
                     f"and c.tile = d.id "
                     f"GROUP BY a.id, c.tile")

    collection["properties"]["bdc:tiles"] = [t['tile'] for t in tiles]

    bands = do_query(f"SELECT b.common_name as band "
                     f"FROM cube_collections a, bands b "
                     f"WHERE '{collection_id}' = a.id and a.id = b.cube_collection "
                     f"GROUP BY b.common_name")

    collection["properties"]["bdc:bands"] = [b['band'] for b in bands]

    cube_collection = \
        do_query(f"SELECT a.grs_schema, b.temporal_schema, b.temporal_composite_unit, b.temporal_composite_t "
                 f"FROM cube_collections a, temporal_composition_schemas b, grs_schemas c "
                 f"WHERE '{collection_id}' = a.id and a.temporal_composition_schema = b.id and a.grs_schema = c.id ")[0]

    collection["properties"]["bdc:tschema"] = cube_collection['temporal_schema']
    collection["properties"]["bdc:tstep"] = cube_collection['temporal_composite_t']
    collection["properties"]["bdc:tunit"] = cube_collection['temporal_composite_unit']

    collection["properties"]["bdc:wrs"] = cube_collection['grs_schema']

    return collection


def get_collections():
    sql = "SELECT  id FROM  cube_collections"
    collections = do_query(sql)

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
        feature['id'] = i['item']
        feature['collection'] = i['cube_collection']

        feature['geometry'] = json.loads(i['geom'])
        feature['bbox'] = bbox(feature['geometry']['coordinates'])

        properties = OrderedDict()

        start = datetime.fromisoformat(str(i['start'])).isoformat()
        properties['bdc:time_aggregation'] = i['type']
        properties['bdc:tile'] = i['tileid']
        properties['datetime'] = f"{start}"
        feature['properties'] = properties

        assets = OrderedDict()
        assets['thumbnail'] = {'href': os.getenv('FILE_ROOT') + i['quicklook']}
        feature['assets'] = assets
        feature['links'] = deepcopy(links)
        feature['links'][0]['href'] += i['cube_collection'] + "/items/" + i['item']
        feature['links'][1]['href'] += i['cube_collection']
        feature['links'][2]['href'] += i['cube_collection']

        feature['assets'] = i['assets']

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
    engine = sqlalchemy.create_engine(connection)
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
