from wmsproxy.wsgi import make_wsgi_app

import logging
log = logging.getLogger(__name__)

application = make_wsgi_app(
    config_cache_dir='cache/',
    max_age_seconds=30*60,
    cartodb_domain='cartodb.com'
)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('requests').setLevel(logging.WARN)

    from mapproxy.util.ext.serving import run_simple
    run_simple('localhost', 5050, application, use_reloader=True, processes=1,
               threaded=True, passthrough_errors=True)

