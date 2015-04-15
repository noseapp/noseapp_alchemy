# -*- coding: utf-8 -*-

from sqlalchemy.orm.session import Session as BaseSession

from noseapp_alchemy import registry
from noseapp_alchemy.exc import InvalidBindKey


class Session(BaseSession):

    def get_bind(self, mapper=None, clause=None):
        if mapper is not None:
            info = getattr(mapper.mapped_table, 'info', {})
            engine_key = info.get('bind_key')

            if engine_key is not None:
                engine = registry.get_engine(engine_key)

                if not engine:
                    raise InvalidBindKey(engine_key)

                return engine

        return BaseSession.get_bind(self, mapper, clause)
