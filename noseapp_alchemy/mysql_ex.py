# -*- coding: utf-8 -*-

from contextlib import contextmanager

from noseapp.core import ExtensionInstaller

from noseapp_alchemy import registry
from noseapp_alchemy.config import Config
from noseapp_alchemy.base import setup_engine
from noseapp_alchemy.base import setup_session
from noseapp_alchemy.constants import DEFAULT_BIND_KEY
from noseapp_alchemy.constants import DEFAULT_POOL_CLASS


DEFAULT_PORT = 3306
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PROTOCOL = 'mysql'

DEFAULT_USE_UNICODE = 1
DEFAULT_CHARSET = 'utf8'

DEFAULT_DNS_PARAMS = {
    'charset': DEFAULT_CHARSET,
    'use_unicode': DEFAULT_USE_UNICODE,
}


class MySQLClient(object):
    """
    Read-write client
    """

    def __init__(self, engine):
        self._engine = engine

    @contextmanager
    def read(self):
        yield self._engine.connect().execute

    @contextmanager
    def write(self):
        connection = self._engine.connect()
        trans = connection.begin()
        try:
            yield connection.execute
            trans.commit()
        except:
            trans.rollback()
            raise


class MySQLEx(object):
    """
    Extension installer
    """

    name = 'mysql'

    config_key = 'ALCHEMY_EX_MYSQL'
    session_config_key = 'ALCHEMY_EX_SESSION'

    client_class = MySQLClient

    def __init__(self, *configs):
        for config in configs:
            setup_engine(**config)

    @classmethod
    def install(cls, app):
        configs = app.config.get(cls.config_key, [])

        for config in configs:
            setup_engine(**config)

        session_options = app.config.get(cls.session_config_key, {})
        setup_session(**session_options)

        installer = ExtensionInstaller(cls, tuple(), {})
        app.shared_extension(cls=installer)

        return installer

    @staticmethod
    def orm_session_configure(**params):
        """
        Setup session or reconfigure
        """
        setup_session(**params)

    def get_client(self, bind_key=DEFAULT_BIND_KEY):
        """
        Get db client by bind key
        """
        return self.client_class(
            registry.get_engine(bind_key),
        )


def make_config():
    """
    Create base config
    """
    return Config(
        db=None,
        user=None,
        password=None,
        host=DEFAULT_HOST,
        port=DEFAULT_PORT,
        bind_key=DEFAULT_BIND_KEY,
        protocol=DEFAULT_PROTOCOL,
        pool_class=DEFAULT_POOL_CLASS,
        dns_params=DEFAULT_DNS_PARAMS,
    )
