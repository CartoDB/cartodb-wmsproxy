import os
import errno
import time

from wmsproxy.viz import tile_params, user_uuids, RequestError
from wmsproxy.config_writer import mapproxy_config, write_mapproxy_config

from mapproxy.util.lock import FileLock

import logging
log = logging.getLogger(__name__)

class ConfigCache(object):
    def __init__(self, cache_dir, max_age_seconds=30*60, cartodb_domain='cartodb.com'):
        self.cache_dir = cache_dir
        self.max_age_seconds =max_age_seconds
        self.cartodb_domain = cartodb_domain

    def _requires_reconf(self, conf_filename):
        """
        Returns True if conf_filename is missing or older then max_age_seconds.
        """
        try:
            mtime = os.path.getmtime(conf_filename)
        except OSError as exc:
            if exc.errno == errno.ENOENT:
                return True
            raise exc

        return (time.time() - self.max_age_seconds) > mtime

    def config(self, user, uuid=None, max_uuids=50):
        conf_filename = os.path.join(self.cache_dir, (uuid or user) + '.yaml')
        if self._requires_reconf(conf_filename):
            with FileLock(conf_filename + '.lck'):
                if self._requires_reconf(conf_filename):
                    log.debug('(re)configure %s for %s', (uuid or "all"), user)
                    if uuid:
                        params = tile_params(user, uuid, self.cartodb_domain)
                        if params is None:
                            return
                        conf = mapproxy_config([params], user=user)

                    else:
                        layers = []
                        for uuid in user_uuids(user, max_uuids=max_uuids, cartodb_domain=self.cartodb_domain):
                            try:
                                params = tile_params(user, uuid, self.cartodb_domain)
                                if params:
                                    layers.append(params)
                                else:
                                    log.warn("found no layer for %s %s", user, uuid)
                            except RequestError as ex:
                                log.warn("faild to query tiler for %s %s: %s", user, uuid, ex)

                        if not layers:
                            return

                        conf = mapproxy_config(layers, user=user)
                    write_mapproxy_config(conf, conf_filename)

        return conf_filename

