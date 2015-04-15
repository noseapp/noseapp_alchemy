# -*- coding: utf8 -*-

from urllib import urlencode

from sqlalchemy import event
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.result import exc
from sqlalchemy.orm import scoped_session

from noseapp_alchemy import registry
from noseapp_alchemy.session import Session
from noseapp_alchemy.constants import DEFAULT_BIND_KEY
from noseapp_alchemy.constants import DEFAULT_POOL_CLASS


AUTO_FLUSH = True
AUTO_COMMIT = False
EXPIRE_ON_COMMIT = True


def ping_connection(connection, connection_record, connection_proxy):
    cursor = connection.cursor()

    try:
        cursor.execute('SELECT 1')
    except:
        raise exc.DisconnectionError()

    cursor.close()


def setup_engine(
        protocol, host, port, db, user,
        password='',
        dns_params='',
        bind_key=DEFAULT_BIND_KEY,
        pool_class=DEFAULT_POOL_CLASS,
        **engine_options):
    """
    :param host: db host
    :param port: db port
    :param db: db name
    :param user: user name
    :param password: user password
    :param protocol: dns protocol
    :param pool_class: pool class (original param name: poolclass)
    :param dns_params: params to dns
    :param engine_options: engine kwargs
    """
    if dns_params and isinstance(dns_params, dict):
        dns_params = '?%s' % urlencode(dns_params)

    dns = '{protocol}://{user}:{password}@{host}:{port}/{database}%s' % dns_params

    engine = create_engine(
        dns.format(
            user=user,
            host=host,
            port=port,
            database=db,
            protocol=protocol,
            password=password,
        ),
        poolclass=pool_class,
        **engine_options
    )

    if pool_class != DEFAULT_POOL_CLASS:
        event.listen(engine, 'checkout', ping_connection)

    registry.register_engine(bind_key, engine)


def setup_session(
        autoflush=AUTO_FLUSH,
        autocommit=AUTO_COMMIT,
        expire_on_commit=EXPIRE_ON_COMMIT,
        **options):
    """
    Setup orm session
    """
    sess = scoped_session(
        sessionmaker(
            class_=Session,
            autoflush=autoflush,
            autocommit=autocommit,
            expire_on_commit=expire_on_commit,
            **options
        ),
    )
    registry.register_session(sess)
