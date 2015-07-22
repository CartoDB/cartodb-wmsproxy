# Uncomment to include standard Python/MapProxy logging configuration
# import os.path
# from logging.config import fileConfig
# here = os.path.abspath(os.path.dirname(__file__))
# fileConfig(os.path.join(here, 'log.ini'))

TILER_URL_TEMPLATE = '%(tiler_protocol)s://%(user_name)s.%(tiler_domain)s:%(tiler_port)s/api/v1/map'
TILE_URL_TEMPLATE = '%(protocol)s://0.%(domain)s/%(user_name)s/api/v1/map/%(layergroupid)s/'
VIZ_URL_TEMPLATE = 'http://%(user)s.cartodb.com/api/v2/viz/%(uuid)s/viz.json'
ALL_VIZ_TEMPLATE = 'http://%(user)s.cartodb.com/api/v1/viz/?tag_name=&q=&page=1&type=table&exclude_shared=false&per_page=%(max)s&table_data=false&o%%5Bupdated_at%%5D=desc&exclude_raster=true'

from wmsproxy.wsgi import make_wsgi_app

application = make_wsgi_app(
    config_cache_dir='cache/',
    max_age_seconds=30*60,
)
