__author__ = 'iljichoi'
import pymongo
import settings

class Pool():

    def __init__(self):
        print 'load db settings...'
        self.__load_settings()
        self.pool = self.__create_connection()
        print 'MongoDB connection is completed'


    def __load_settings(self):
        if settings.MONGODB is None:
            err_msg = '''
            MONGODB setting is None! If you want to use mongodb,
            you must write MONGODB setting information as dictionary type.
            '''
            raise Exception(err_msg)
        for k, v in settings.MONGODB.iteritems():
            setattr(self, k, v)

    def __create_connection(self):
        return pymongo.MongoClient(
            host=self.host,
            port=self.port, maxPoolSize=self.MAX_POOL_SIZE)

    def __get_connection_to_collection(self):
        _db = self.pool.get_database(self.db)
        return _db.get_collection(self.collection)

    def insert_blog_to_db(self, info):
        coll_connection = self.__get_connection_to_collection()
        coll_connection.insert(info)
