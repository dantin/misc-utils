# -*- coding=utf-8 -*-
""" 封装MongoDB的操作
1. 封装数据库操作(INSERT,FIND,UPDATE)
2. 函数执行完MONGODB操作后关闭数据库连接

注意:不要直接使用Mongo和Collection,需要结合mongo_connection一起使用.

Usage::
    >>>s_db = Mongo()
    >>>@mongo_connection(['s_db'])
    ...: def test():
    ...:     print s_db.test.insert({'a': 1, 'b': 2})
    ...:
"""

from functools import wraps

from pymongo.database import Database

try:
    from pymongo import MongoClient
except ImportError:
    # 好像2.4之前的pymongo都没有MongoClient,现在官网已经把Connection抛弃了
    import warnings

    warnings.warn("Please update the latest version of pymongo version")
    from pymongo import Connection as MongoClient


class Mongo(object):
    """封装数据库操作"""

    def __init__(self, host='localhost', port=27017, database='test', username='', password='',
                 max_pool_size=10, timeout=10):
        self.host = host
        self.port = port
        self.max_pool_size = max_pool_size
        self.timeout = timeout
        self.database = database
        self.username = username
        self.password = password

    @property
    def connect(self):
        # 这里是为了使用类似"db.集合.操作"的操作的时候才会生成数据库连接,其实pymongo已经实现了进程池,也可以把这个db放在__init__里面,
        # 比如把db关掉有其他的数据库调用连接又会生成,并且不影响使用.这里只是想每次执行数据库生成一个连接用完关掉
        connection = MongoClient(self.host, self.port, maxPoolSize=self.max_pool_size,
                                 connectTimeoutMS=60 * 60 * self.timeout)
        if self.username and self.password:
            # Note: no need to urllib.quote_plus the password here as a parameter
            if connection[self.database].authenticate(self.username, self.password):
                raise RuntimeError('authentication error, user: %s!' % self.username)

        return connection

    def __getitem__(self, collection):
        # 为了兼容db[集合].操作的用法
        return self.__getattr__(collection)

    def __getattr__(self, collection_or_func):
        db = self.connect[self.database]
        if collection_or_func in Database.__dict__:
            # 当调用的是db的方法就直接返回
            return getattr(db, collection_or_func)
        # 否则委派给Collection
        return Collection(db, collection_or_func)


class Collection(object):
    def __init__(self, db, collection):
        self.collection = getattr(db, collection)

    def __getattr__(self, operation):
        # 这个封装只是为了拦截一部分操作,不符合的就直接raise属性错误
        control_type = ['disconnect', 'insert', 'update', 'find', 'find_one', 'count']
        if operation in control_type:
            return getattr(self.collection, operation)
        raise AttributeError(operation)


def mongo_connection(dbs=None):
    """自动关闭mongodb数据库连接
    :param dbs : 在执行函数里面使用的db的名字(大部分是db，也会有s_db)
    """
    if not dbs:
        dbs = ['db']

    def _deco(func):
        @wraps(func)
        def _call(*args, **kwargs):
            result = func(*args, **kwargs)
            for db in dbs:
                try:
                    # func.func_globals[db].connect.close()
                    func.__globals__[db].connect.close()
                except KeyError:
                    pass
            return result

        return _call

    return _deco
