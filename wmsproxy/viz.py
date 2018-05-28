import requests
import json

TILER_URL_TEMPLATE = '%(tiler_protocol)s://%(user_name)s.%(tiler_domain)s:%(tiler_port)s/api/v1/map'
TILE_URL_TEMPLATE = '%(protocol)s://0.%(domain)s/%(user_name)s/api/v1/map/%(layergroupid)s/'
VIZ_URL_TEMPLATE = 'http://%(user)s.%(domain)s/api/v2/viz/%(uuid)s/viz.json'
ALL_VIZ_TEMPLATE = 'http://%(user)s.%(domain)s/api/v1/viz/?tag_name=&q=&page=1&types=table,derived&exclude_shared=false&per_page=%(max)s&table_data=false&o%%5Bupdated_at%%5D=desc&exclude_raster=true'

import logging
log = logging.getLogger(__name__)

class RequestError(Exception):
    pass

def tiler_url(layer):
    return TILER_URL_TEMPLATE % {
        'tiler_protocol': layer['options']['tiler_protocol'],
        'user_name': layer['options']['user_name'],
        'tiler_domain': layer['options']['tiler_domain'],
        'tiler_port': layer['options']['tiler_port']
    }

def layer_definition(layer):
    for l in layer['options']['layer_definition']['layers']:
        l['type'] = l['type'].lower()

    return layer['options']['layer_definition']

def tile_url(tiler_url, layer_definition, user):
    try:
        resp = requests.post(
            tiler_url,
            data=json.dumps(layer_definition),
            headers={
                'Content-type': 'application/json',
                'Accept': 'application/json'
            }
        )
    except requests.exceptions.RequestException as exc:
        raise RequestError("unable to query tiler", exc)

    if not resp.ok:
        raise RequestError("unable to query tiler", resp)

    data = resp.json()
    url = TILE_URL_TEMPLATE % {
        'protocol': 'http',
        'domain': data['cdn_url']['http'],
        'user_name': user,
        'layergroupid': data['layergroupid'],
    }

    return url, data['last_updated']

def user_uuids(user, max_uuids=50, cartodb_domain='cartodb.com'):
    url = ALL_VIZ_TEMPLATE % {'user': user, 'max': max_uuids, 'domain': cartodb_domain}
    try:
        resp = requests.get(url)
    except requests.exceptions.RequestException as exc:
        raise RequestError("unable to retreive viz.json", exc)
    if not resp.ok:
        raise RequestError("unable to retreive viz.json", resp)

    try:
        viz_doc = resp.json()
    except ValueError as e:
        raise RequestError("Error parsing viz.json", e)
    uuids = [viz['id'] for viz in viz_doc['visualizations'][:max_uuids]]
    return uuids

def tile_params(user, uuid, cartodb_domain='cartodb.com'):
    url = VIZ_URL_TEMPLATE % {'user': user, 'uuid': uuid, 'domain': cartodb_domain}
    try:
        resp = requests.get(url)
    except requests.exceptions.RequestException as exc:
        raise RequestError("unable to retreive viz.json", exc)
    if not resp.ok:
        raise RequestError("unable to retreive viz.json", resp)

    try:
        viz_doc = resp.json()
    except ValueError as e:
        raise RequestError("Error parsing viz.json", e)

    bounds = None
    # clip bounds to -180,-90,180,90
    if 'bounds' in viz_doc and viz_doc['bounds']:
        bounds = [
            max(viz_doc['bounds'][0][1], -180),
            max(viz_doc['bounds'][0][0], -90),
            min(viz_doc['bounds'][1][1], 180),
            min(viz_doc['bounds'][1][0], 90),
        ]

    for layer in viz_doc['layers']:
        if layer['type'] == 'layergroup':
            turl = tiler_url(layer)
            ldef = layer_definition(layer)
            url, last_updated = tile_url(turl, ldef, user=user)

            return {
                'url': url,
                'last_updated': last_updated,
                'bounds': bounds,
                'title': viz_doc['title'],
            }
        if layer['type'] == 'namedmap':
            turl = tiler_url(layer) + '/named/' + layer['options']['named_map']['name']
            ldef = layer['options']['named_map']['params']
            url, last_updated = tile_url(turl, ldef, user=user)

            return {
                'url': url,
                'last_updated': last_updated,
                'bounds': bounds,
                'title': viz_doc['title'],
            }

if __name__ == '__main__':
    viz_urls = [
        # spencer http://osm2.cartodb.com/viz/fda70aae-a7a5-11e4-96f0-0e0c41326911/embed_map
        'https://osm2.cartodb.com/api/v2/viz/fda70aae-a7a5-11e4-96f0-0e0c41326911/viz.json',
        # # ratrace http://osm2.cartodb.com/viz/feeaae54-9e89-11e4-ba3a-0e853d047bba/embed_map
        # 'https://osm2.cartodb.com/api/v2/viz/feeaae54-9e89-11e4-ba3a-0e853d047bba/viz.json',
        # # openacces jornals https://scinoptica.cartodb.com/viz/89012366-2f59-11e4-be5a-0e230854a1cb/public_map
        # 'https://scinoptica.cartodb.com/api/v2/viz/89012366-2f59-11e4-be5a-0e230854a1cb/viz.json',
        # # bogota en 3d http://gkudos.cartodb.com/u/gkudos-developer/viz/a637d2ba-3f4c-11e4-a39d-0e230854a1cb/embed_map
        # 'http://gkudos.cartodb.com/u/gkudos-developer/api/v2/viz/a637d2ba-3f4c-11e4-a39d-0e230854a1cb/viz.json'
    ]

    # for viz_url in viz_urls:
    #     pprint(tile_params(viz_url))
    #     print '----'


    user = 'gce01'
    for uuid in user_uuids(user, cartodb_domain='cartodb.com', max_uuids=50):
        try:
            print tile_params(user, uuid)
        except RequestError as ex:
            print ex
