__author__ = 'marcotagliabue'

import sys
import logging

import pymongo
from pymongo.errors import DuplicateKeyError

import configuration


class MongoManager():
    def __init__(self, name_db):
        """This will be called each time we receive stream data"""
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

    def find(self, collection, query, limite=sys.maxsize,project={}):
        return self.db[collection].find(query).limit(limite)

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
    
    # knowledge extractor pipeline method
    def getExpertTypes(self,experimentId):
        collection="experiment"
        query={
            "_id":experimentId
        }
        experiment = list(self.find(collection,query,project={"expert_types":1}))[0]
        return experiment["expert_types"]

    def getSeeds(self,query):
        collection = "seeds"
        return self.find(collection,query)

    def getCandidates(self,query):
        collection = "rank_candidates"
        return self.find(collection,query)

    def getMentions(self,query):
        collection = "entity"
        return self.find(collection,query,project={"spot":1,"types":1,"label":1})
    
    def getMentionType(self,query):
        collection = "entity"
        return self.find(collection,query,project={"types":1})

    def saveScores(self,scores,id_experiment):
        collection = "rankings"
        for k,v in scores.items():
            score = {
                "handle":k,
                "score":v,
                "experiment_id":id_experiment
            }
            self.write_mongo(collection,score)


if __name__ == '__main__':
    print("mongo_manager")
