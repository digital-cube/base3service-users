# coding= utf-8

import contextlib

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from sqlalchemy.engine.url import URL
import os

def make_database_url(db_type, name, host, port, username, password, charset='utf8'):
    """Create database url"""

    if db_type == 'mysql':
        return URL(drivername='mysql+mysqldb', username=username, password=password, host=host, port=port,
                   database=name, query={'charset': charset})
    if db_type == 'postgresql':
        return URL(drivername='postgresql+psycopg2', username=username, password=password, host=host, port=port,
                   database=name, query={'client_encoding': charset})
    if db_type == 'sqlite':
        return URL(drivername='sqlite', database='{}.db'.format(name))
    else:
        raise NameError("Unknown database type: {}".format(db_type))


telmekom_sql_base = declarative_base()
telmekom_orm = None


class _telmekom_orm(object):
    __instance = None

    def __new__(cls, sql_address, orm_base, **kwargs):
        if _telmekom_orm.__instance is None:
            _telmekom_orm.__instance = object.__new__(cls)
            cls.__db_url = sql_address
            cls.__engine = create_engine(cls.__db_url, echo=False, **kwargs)
            cls.__session_factory = sessionmaker(bind=cls.__engine)
            cls.__scoped_session = scoped_session(cls.__session_factory)
            cls.__session = cls.__scoped_session()
            cls.__base = orm_base

        return _telmekom_orm.__instance

    def session(self):
        __session_factory = sessionmaker(bind=self.__engine)
        __scoped_session = scoped_session(__session_factory)
        return __scoped_session()


def activate_orm():
    global telmekom_orm
    global telmekom_sql_base


    from base import config
    cfg = config.conf['mysql']

    _db_url = make_database_url(cfg['db_type'], cfg['db_name'], cfg['db_host'], cfg['db_port'],
                                cfg['db_user'], cfg['db_password'], cfg['db_charset'])

    telmekom_orm = _telmekom_orm(_db_url, telmekom_sql_base)


@contextlib.contextmanager
def telmekom_orm_session():
    global telmekom_orm
    if not telmekom_orm:
        activate_orm()

    _session = telmekom_orm.session()
    try:
        yield _session
    except:
        _session.rollback()
        raise
    finally:
        _session.close()

