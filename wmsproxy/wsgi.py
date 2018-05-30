import re
import mapproxy.version

import mapproxy.request.wms
from mapproxy.request import Request
from mapproxy.response import Response
from mapproxy.wsgiapp import make_wsgi_app as make_mapproxy_wsgi_app
from mapproxy.exception import RequestError as MPRequestError

from wmsproxy.config_cache import ConfigCache
from wmsproxy.viz import RequestError

import logging
log = logging.getLogger(__name__)

uuid_path_re = re.compile(
    '^/[a-f0-9]{,8}-[a-f0-9]{,4}-[a-f0-9]{,4}-[a-f0-9]{,4}-[a-f0-9]{,12}', re.IGNORECASE)

api_path_re = re.compile('^/api/v2/wms/(.*)')

class WMSProxy(object):

    def __init__(self, config_cache, max_uuids_per_user=50):
        self.config_cache = config_cache
        self.max_uuids_per_user = max_uuids_per_user
        self.logger = log

    def __call__(self, environ, start_response):
        req = Request(environ)
        return self.handle(req)(environ, start_response)

    def handle(self, req):
        host = req.environ['HTTP_HOST']
        user = host.split(".",1)[0]
        api = api_path_re.search(req.path)
        if api != None:
            req.environ['SCRIPT_NAME'] = '/api/v2/wms/'
            req.environ['PATH_INFO'] = '/' + api.groups()[0]
        uuid = None
        if uuid_path_re.match(req.path):
            uuid = req.pop_path()

        if not user:
            return Response('not found', status=404)

        req.environ['mapproxy.authorize'] = self.check_single_layer
        return self.create_app(user, uuid)

    def check_single_layer(self, service, layers=[], environ=None, **kw):
        if service == 'wms.map':
            if len(layers) > 1:
                # raise req error to get proper WMS service exception
                mreq = mapproxy.request.wms.wms_request(
                    environ['mapproxy.request'])
                raise MPRequestError(
                    'Layer composition is not supported. Please request only a single layer.',
                    request=mreq,
                )
        return {'authorized': 'full'}

    def create_app(self, user, uuid):
        try:
            mapproxy_conf = self.config_cache.config(
                user, uuid, self.max_uuids_per_user)
        except RequestError:
            log.exception('unable to query config')
            return Response('service unavailable', status=503)

        if not mapproxy_conf:
            return Response('not found', status=404)

        log.debug('initializing project %s', mapproxy_conf)
        return make_mapproxy_wsgi_app(mapproxy_conf)


def make_wsgi_app(config_cache_dir, max_age_seconds=30 * 60, cartodb_domain='cartodb.com'):
    cache = ConfigCache(config_cache_dir, max_age_seconds=max_age_seconds, cartodb_domain=cartodb_domain)
    app = WMSProxy(cache)

    return app

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('requests').setLevel(logging.WARN)

    app = make_wsgi_app('/tmp')
    from mapproxy.util.ext.serving import run_simple
    run_simple('localhost', 5050, app, use_reloader=True, processes=1,
               threaded=True, passthrough_errors=True)
