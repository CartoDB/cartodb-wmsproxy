from wmtsproxy_restapi.app import create_app, DefaultConfig
import os.path
from logging.config import fileConfig

here = os.path.abspath(os.path.dirname(__file__))
fileConfig(os.path.join(here, 'api_logging.ini'))


class Config(DefaultConfig):
    CSV_FILE = os.path.join(here, 'services.csv')


application = create_app(Config)
