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
        query.update({"hub":False})
        return list(self.find(collection,query))
    
    def getHubs(self,query):
        collection = "seeds"
        query.update({"hub":True})
        return list(self.find(collection,query))

    def getCandidates(self,query):
        collection = "rank_candidates"
        return list(self.find(collection,query))

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
    
    def getResults(self,experiment_id,limit=False,skip=None):
        collection = "rankings"
        query = {
            "experiment_id":experiment_id,
            "score":{"$ne":float('nan')}
        }
        if(limit):
            if(skip!=None):
                return self.find(collection,query).sort("score",-1).limit(20).skip(skip)

            return self.find(collection,query).sort("score",-1).limit(20)
        else:
            return self.find(collection,query).sort("score",-1)
    
    def register_evaluation(self,query,update):
        collection="evaluation"
        return self.db[collection].update(query,update,upsert=True)
    
    def get_evaluations(self,experiment_id):
        collection="evaluation"
        query = {
            "experiment":experiment_id
        }
        return self.find(collection,query)
    
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
    
    def get_recipe(self,name):
        collection = "recipe"
        query = {
            "name":name
        }
        return self.find(collection,query)
    
    def store_seeds(self,seeds,experiment_id):
        collection = "seeds"
        for seed in seeds:
            s = {
                "id_experiment":experiment_id,
                "starting":True,
                "hub":False,
                "handle":seed
            }
            self.db[collection].insert(s)

    def store_feature_ast_vector(self,fv,experiment_id):
        collection = "seeds"
        for handle,row in fv.itertuples():
            query={
                "id_experiment":experiment_id,
                "handle":handle
            }
            update={
                "$set":{
                    "fv":row
                }
            }
        return self.db[collection].update(query,update)

    def store_hubs(self,hubs,experiment_id):
        collection = "seeds"
        for hub in hubs:
            h = {
                "id_experiment":experiment_id,
                "starting":True,
                "hub":True,
                "handle":hub
            }
            self.db[collection].insert(h)
    
    def store_candidates(self,candidates,experiment_id):
        collection = "seeds"
        for cand in candidates:
              c = {
                "id_experiment":experiment_id,
                "starting":False,
                "hub":False,
                "handle":cand["handle"],
                "origin":cand["origin"]
              }
              self.db[collection].insert(c)
    
    def get_unranked_candidates(self,experiment_id):
        collection = "seeds"
        query = {
            "id_experiment":experiment_id,
            "starting":False,
            "hub":False
        }
        return list(self.find(collection,query))

    def get_mention_count_all(self,experiment_id):
        collection = "entity"
        query = ([{"$match":{"id_experiment":experiment_id,"types":{"$not":{"$size":0}}}},{"$project":{"seed":1,"types":1}},{"$unwind":"$types"},{"$group":{_id:"$types",count:{"$sum":1}}},{"$sort":{count:-1}}])
        return list(self.db[collection].aggregate(query))
    
    def get_mention_count_by_seeds(self,experiment_id,seed_ids):
        collection = "entity"
        query = ([{"$match":{"id_experiment":experiment_id,"seed":{"$in":seed_ids},"types":{"$not":{"$size":0}}}},{"$project":{"seed":1,"types":1}},{"$unwind":"$types"},{"$group":{"_id":"$types","count":{"$sum":1}}},{"$sort":{"count":-1}}])
        return list(self.db[collection].aggregate(query))


if __name__ == '__main__':
    db_manager = MongoManager(configuration.db_name)
