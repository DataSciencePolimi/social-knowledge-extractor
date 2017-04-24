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
            pass
            #logging.error("")

    def write_mongo_no_duplicates(self, collection, data, unique_key):
        self.db[collection].update({unique_key: data[unique_key]}, data, upsert=True)

    def find_one(self, collection):
        return self.db[collection].find_one()

    def find(self, collection, query, limite=sys.maxsize,project={}):
        return self.db[collection].find(query)

    def delete_element(self, collection, query):
        return self.db[collection].delete_many(query)

    def update(self, collection, query, data):
        return self.db[collection].update(query, data, True)

    def aggregate(self, collection, query):
        return self.db[collection].aggregate(query)

    def drop_collection(self, collection):
        return self.db.drop_collection(collection)
    
    def get_dandelion_keys(self):
        query = {
            "service":"dandelion"
        }
        return self.db["application_keys"].find(query)
    
    def get_twitter_keys(self):
        query = {
            "service":"twitter"
        }
        return self.db["application_keys"].find(query)
    
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
    
    def getExperiment(self,experiment_id):
        collection = "experiment"
        query={
            "_id":experiment_id
        }
        return self.find(collection,query)
    
    def getResults(self,experiment_id,limit=False):
        collection = "rankings"
        query = {
            "experiment_id":experiment_id,
            "score":{"$ne":float('nan')}
        }
        if(limit):
            return self.find(collection,query).sort("score",-1).limit(20)
        else:
            return self.find(collection,query).sort("score",-1)
    
    def register_evaluation(self,query,update):
        collection="evaluation"
        return self.db[collection].update(query,update,upsert=True)
    
    def get_user_twitter_tokens(self,experiment_id):
        experiment = list(self.getExperiment(experiment_id))[0]
        user_id = experiment["user_id"]
        query = {
            "_id":user_id
        }
        user = list(self.find("auth_users",query))[0]
        tokens = {
            "access_token":user["access_token"],
            "access_token_secret":user["access_token_secret"]
        }
        return tokens

    def update_user_twitter(self,user_id,access_token,access_token_secret,profile_img):
        collection="auth_users"
        query={
            "_id":user_id
        }
        update={
            "$set":{
                "access_token":access_token,
                "access_token_secret":access_token_secret,
                "profile_img":profile_img
            }
        }
        return self.db[collection].update(query,update)

if __name__ == '__main__':
    db_manager = MongoManager(configuration.db_name)
