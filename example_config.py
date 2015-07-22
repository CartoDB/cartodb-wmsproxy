# Uncomment to include standard Python/MapProxy logging configuration
# import os.path
# from logging.config import fileConfig
# here = os.path.abspath(os.path.dirname(__file__))
# fileConfig(os.path.join(here, 'log.ini'))

from wmsproxy.wsgi import make_wsgi_app

application = make_wsgi_app(
    config_cache_dir='cache/',
    max_age_seconds=30*60,
    cartodb_domain='cartodb-staging.com'
)
