import re
import yaml

from mapproxy.util.fs import write_atomic


def mapproxy_config(layers, user):
    conf = {
        'services': {
            'wmts': {
                'md': {'title': 'CartoDB WMTS for %s' % user, },
            },
            'demo': {},
            'wms': {
                'md': {'title': 'CartoDB WMS for %s' % user, },
                'srs': ['EPSG:4326', 'EPSG:3857', 'EPSG:900913'],
            },
        },
        'caches': {},
        'sources': {},
        'layers': [],
        'grids': {
            'webmercator': {
                'base': 'GLOBAL_WEBMERCATOR',
                'srs': 'EPSG:3857',
            },
        },
    }

    for layer in layers:
        title = layer['title']
        name = sanitize(title)
        conf['caches'][name] = {
                'sources': [name],
                'grids': ['webmercator'],
                'disable_storage': True,
                'concurrent_tile_creators': 4,
        }
        conf['layers'].append({
            'name': name,
            'title': title,
            'sources': [name],
        })

        conf['sources'][name] = {
            'type': 'tile',
            'url': layer['url'] + '%(tms_path)s.png',
            'transparent': True,
            'grid': 'webmercator',
        }

        # TODO
        if False:
        # if bbox:
            conf['sources'][name]['coverage'] = {
                'bbox': layer['bounds'],
                'srs': 'EPSG:4326',
            }

    return conf


non_safechar = re.compile('[^a-zA-Z0-9_-]+')

def sanitize(name):
    return non_safechar.sub('', name)


def write_mapproxy_config(mapproxy_conf, filename):
    content = yaml.safe_dump(mapproxy_conf, default_flow_style=False)
    write_atomic(filename, content)
