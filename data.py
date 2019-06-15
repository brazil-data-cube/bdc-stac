import sqlalchemy
import os


def bbox_querie(bbox, start=0, count=10):
    sql = "SELECT s.*, DATE_FORMAT(s.`Date`,'%%Y-%%m-%%dT%%H:%%i:%%s') as `Date`, " \
          "DATE_FORMAT(s.`IngestDate`,'%%Y-%%m-%%dT%%H:%%i:%%s') as `IngestDate` " \
          "FROM Scene AS s, Product AS p WHERE "
    where = list()

    where.append('s.`SceneId` = p.`SceneId`')
    try:
        for x in bbox.split(','):
            float(x)
        min_x, min_y, max_x, max_y = bbox.split(',')

        bbox = ""
        bbox += "(({} <= `TR_Longitude` and {} <=`TR_Latitude`)".format(min_x, min_y)
        bbox += " or "
        bbox += "({} <= `BR_Longitude` and {} <=`TL_Latitude`))".format(min_x, min_y)
        bbox += " and "
        bbox += "(({} >= `BL_Longitude` and {} >=`BL_Latitude`)".format(max_x, max_y)
        bbox += " or "
        bbox += "({} >= `TL_Longitude` and {} >=`BR_Latitude`))".format(max_x, max_y)

        where.append("(" + bbox + ")")

    except:
        raise (InvalidBoundingBoxError())

    where = " and ".join(where)

    sql += where

    sql += " GROUP BY s.`SceneId` ORDER BY `Date` DESC"

    sql += " LIMIT {},{}".format(start, count)

    result = do_query(sql)


def get_datacubes():
    sql = "SELECT datacube FROM  `datacubes`"
    datacubes = do_query(sql)
    return datacubes


def make_geojson(data, totalResults, searchParams, output='json'):
    geojson = dict()
    geojson['totalResults'] = totalResults
    geojson['type'] = 'FeatureCollection'
    geojson['features'] = []
    for i in data:
        feature = dict()
        feature['type'] = 'Feature'

        geometry = dict()
        geometry['type'] = 'Polygon'
        geometry['coordinates'] = [
            [[i['TL_Longitude'], i['TL_Latitude']],
             [i['BL_Longitude'], i['BL_Latitude']],
             [i['BR_Longitude'], i['BR_Latitude']],
             [i['TR_Longitude'], i['TR_Latitude']],
             [i['TL_Longitude'], i['TL_Latitude']]]
        ]

        feature['geometry'] = geometry
        properties = dict()

        for key, value in i.items():
            if key != 'SceneId' and key != 'IngestDate':
                properties[key.lower()] = value

        feature['properties'] = properties
        geojson['features'].append(feature)

    return geojson


def do_query(sql):
    connection = 'mysql://{}:{}@{}/{}'.format(os.environ.get('DB_USER'),
                                              os.environ.get('DB_PASS'),
                                              os.environ.get('DB_HOST'),
                                              os.environ.get('DB_NAME'))
    engine = sqlalchemy.create_engine(connection)
    result = engine.execute(sql)
    result = result.fetchall()
    engine.dispose()
    return [dict(row) for row in result]


class InvalidBoundingBoxError(Exception):
    pass
