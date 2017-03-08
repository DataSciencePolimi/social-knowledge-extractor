__author__ = 'marcotagliabue'

import pymongo
from pymongo.errors import DuplicateKeyError
import configuration
import sys
import logging


class MongoManager():
    def __init__(self, name_db):
        """This will be called each time we receive stream Data"""
        client = pymongo.MongoClient(configuration.address_local, configuration.port_local)
        self.db = client[name_db]

    def write_mongo(self, collection, data):
        try:
            return self.db[collection].insert(data)
        except DuplicateKeyError as e:
            logging.error(e)

    def write_mongo_no_duplicates(self, collection, data, unique_key):
        self.db[collection].update({unique_key: data[unique_key]}, data, upsert=True)

    def find_one(self, collection):
        return self.db[collection].find_one()

    def find(self, collection, *query, limite=sys.maxsize):
        if (len(query) == 2):
            return self.db[collection].find(query[1]).limit(limite)
        else:
            return self.db[collection].find(query[0]).limit(limite)

    def delete_element(self, collection, query):
        return self.db[collection].delete_many(query)

    def update(self, collection, query, data):
        return self.db[collection].update(query, data, True)

    def aggregate(self, collection, query):
        return self.db[collection].aggregate(query)

    def drop_collection(self, collection):
        return self.db.drop_collection(collection)

    # Avoid duplicates based on the key
    def create_index(self, collection, key):
        unique = True
        self.db[collection].create_index(key, unique=unique)

    def delete_one(self, collection, query):
        result = self.db[collection].delete_one(query)
        if (result.deleted_count > 0):
            return True
        else:
            return False

    def delete_many(self, collection, query):
        result = self.db[collection].delete_many(query)
        if (result.deleted_count > 0):
            return True
        else:
            return False


if __name__ == '__main__':
    print("mongo_manager")
