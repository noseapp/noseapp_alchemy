============
Installation
============

::

    pip install noseapp_alchemy


Install extension from app
--------------------------

config module ::

    from noseapp.ext.alchemy.mysql_ex import make_config

    MY_DB = make_config()

    MY_DB.configure(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='',
        db='target',
        protocol='mysql',
        # pool_size=POOL_SIZE,
        # pool_class=POOL_CLASS,
        # strategy=ENGINE_STRATEGY,
        # max_overflow=MAX_OVERFLOW,
        # bind_key=DB_BIND_KEY,
    )

    ALCHEMY_EX_MYSQL = (
        MY_DB,
    )

    ALCHEMY_EX_SESSION = {}

    etc...


app module ::

    from noseapp import NoseApp
    from noseapp.ext.alchemy import MySQLEx


    class MyApp(NoseApp):

        def initialize(self):
            MySQLEx.install(self)


suite ::

    from noseapp import Suite
    from noseapp import TestCase


    suite = Suite(__name__, require=['mysql'])


    class MyTestCase(TestCase):

        def setUp(self):
            self.db = self.mysql.get_client()
            # get by bind key
            self.db = self.mysql.get_client('bind key')

        def test(self):
            with self.db.read() as execute:
                result = execute('SELECT 1').fetchone()
            self.assertTrue(result)


Usage ORM
---------

::

    from sqlalchemy import Column
    from sqlalchemy import String
    from sqlalchemy import Integer

    from noseapp.ext.alchemy.orm import BaseModel


    class MyModel(BaseModel):
        class Meta:
            # bind = 'bind key from db settings'
            table = 'table name'

    id = Column(Integer, autoincrement=True, nullable=False, primary_key=True)
    name = Column(String(255), nullable=False, default='Name')


Create new object
-----------------

::

    obj = MyModel.create(name='Hello World!')


Update object
-------------

::

    obj = MyModel.objects.get(1)
    obj.update(name='Hello!')


Get objects by
--------------

::

    objects = MyModel.getlist_by(name='Hello')
    obj = MyModel.object.get_by(name='Hello')


Etc...See orm module...
