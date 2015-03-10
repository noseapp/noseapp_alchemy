# -*- coding: utf-8 -*-

"""
Модуль для работы с ORM sql alchemy
"""

import logging
from contextlib import contextmanager

from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.ext.declarative import declarative_base

from noseapp_alchemy import registry
from noseapp_alchemy.exc import NotFound
from noseapp_alchemy.constants import DEFAULT_BIND_KEY


logger = logging.getLogger(__name__)

Session = registry.get_session()


@contextmanager
def session_scope(rollback=True):
    """
    Контекстный менеджер для работы с сессией
    """
    session = Session()
    try:
        yield session
    except:
        if rollback:
            session.rollback()
        raise
    finally:
        session.close()


def dict_info(params):
    """
    Переводит словарь параметров в строковое представоение

    :param params(dict): словарь с параметрами
    """
    return u', '.join([u'%s=%s' % p for p in params.items()])


class StaticProperty(property):
    """
    Делает метод класса "статическим" свойством
    """

    def __get__(self, instance, cls):
        return classmethod(self.fget).__get__(instance, cls)()


class ModelObjects(object):
    """
    Класс реализует интерфейс для осуществления
    операций над группой объектов модели
    """

    DEFAULT_OFFSET = 0
    DEFAULT_LIMIT = 100

    def __init__(self, model):
        self.__model = model

    def get(self, pk):
        """
        Получение объекта по первичному ключу
        """
        with session_scope(rollback=False) as session:
            obj = session.query(self.__model).get(pk)

        if obj:
            return obj

        raise NotFound(
            u'object <{} pk={}> not found'.format(self.__model.__name__, id),
        )

    def get_by(self, **params):
        """
        Получение объекта по фильтрам
        """
        with session_scope(rollback=False) as session:
            obj = session.query(self.__model).filter_by(**params).first()

        if obj:
            return obj

        raise NotFound(
            u'object <{} {}> not found'.format(self.__model.__name__, dict_info(params)),
        )

    def getlist(self, offset=DEFAULT_OFFSET, limit=DEFAULT_LIMIT):
        """
        Получение списка всех объектов
        """
        with session_scope(rollback=False) as session:
            result = session.query(self.__model).offset(offset).limit(limit).all()

        return result

    def getlist_by(self, offset=DEFAULT_OFFSET, limit=DEFAULT_LIMIT, **params):
        """
        Получение списка по фильтрам
        """
        with session_scope(rollback=False) as session:
            result = session.query(self.__model).filter_by(**params).offset(offset).limit(limit).all()

        return result

    def update_by(self, by, **params):
        """
        Обновление объектов по параметрам
        """
        with session_scope() as session:
            objects = session.query(self.__model).filter_by(**by).all()

        for obj in objects:
            for k, v in params.items():
                setattr(obj, k, v)

            with session_scope() as session:
                session.add(obj)
                session.commit()
                session.refresh(obj)

        return objects

    def remove_by(self, **params):
        """
        Удаление объектов по параметрам
        """
        with session_scope() as session:
            objects = session.query(self.__model).filter_by(**params).all()

        for obj in objects:
            with session_scope() as session:
                session.delete(obj)
                session.commit()


class ModelCRUD(object):
    """
    Класс расширяет возможности BaseModel
    для упрощения работы с CRUD операциями
    """

    def __init__(self, **params):
        """
        Инициализатор нового объекта модели
        """
        logger.debug('create new object of model {}'.format(self.__class__.__name__))

        for k, v in params:
            setattr(self, k, v)

    @StaticProperty
    def query(cls):
        return Session.query_property(cls)

    @StaticProperty
    def objects(cls):
        return ModelObjects(cls)

    @classmethod
    def create(cls, **params):
        instance = cls(**params)

        with session_scope() as session:
            session.add(instance)
            session.commit()
            session.refresh(instance)

        return instance

    def to_dict(self):
        """
        Конвертирует данные модели в словарь
        """
        return dict(
            (k, self.__dict__[k])
            for k in self.__dict__
            if not k.startswith('_')
        )

    def update(self, **params):
        """
        Обновление текущего объекта
        """
        with session_scope() as session:

            for k, v in params.items():
                setattr(self, k, v)

            session.add(self)
            session.commit()
            session.refresh(self)

    def remove(self):
        """
        Удаление объекта по id
        """
        with session_scope() as session:
            session.delete(self)
            session.commit()

    def __repr__(self):
        if hasattr(self, 'id'):
            return '<{} id={}>'.format(self.__class__.__name__, self.id or 'NULL')

        return '<{}>'.format(self.__class__.__name__)


def mount_meta(meta, cls):
    """
    Монтирует свойства из класса Meta в класс
    модели, как это привычно видеть алхимии
    """
    model_cls = cls.__mro__[0]

    table_name = getattr(meta, 'table', None)

    if table_name is not None:
        setattr(model_cls, '__tablename__', table_name)


class BoundDeclarativeMeta(DeclarativeMeta):
    """
    Расширяет конфигурацию модели дополняя ее классом Meta
    и возможностью монтировать модели к различным движкам
    """

    def __init__(self, name, bases, d):
        meta = d.pop('Meta', None)

        if meta is not None:
            bind_key = getattr(meta, 'bind', DEFAULT_BIND_KEY)
            mount_meta(meta, self)
        else:
            bind_key = DEFAULT_BIND_KEY

        DeclarativeMeta.__init__(self, name, bases, d)

        try:
            self.__table__.info['bind_key'] = bind_key
        except AttributeError:  # при создании декларативного
            # класса еще не будет атрибута __table__, поэтому эта
            # ситация является нормальной
            pass


BaseModel = declarative_base(cls=ModelCRUD, metaclass=BoundDeclarativeMeta)
