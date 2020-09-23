from wmtsproxy.wsgi import make_wsgi_app
import os.path
from logging.config import fileConfig

here = os.path.abspath(os.path.dirname(__file__))
fileConfig(os.path.join(here, 'mapproxy_logging.ini'))


application = make_wsgi_app(
    configs_path=os.path.join(here, 'tmp_configs'),
    base_file=os.path.join(here, 'mapproxy_base.yaml'),
    csv_file=os.path.join(here, 'services.csv'))
