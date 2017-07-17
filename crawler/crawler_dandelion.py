__author__ = 'marcotagliabue'
import math
import logging
import pprint
import json
from dandelion import DataTXT

from dandelion.base import DandelionException

import configuration
from utils import mongo_manager
from model import tweets_chunk


class CrawlDandelion:
    def __init__(self, one_dandelion_key,db_manager):
        self.db_manager = db_manager
        self.one_dandelion_key = one_dandelion_key
        ontology_file = open('crawler/dbpedia_ontology.json')
        ontology_content = ontology_file.read()
        ontology = json.loads(ontology_content)["owl:Thing"]
        self.ontology = ontology
    
    def start(self,id_experiment):
        if self.one_dandelion_key:
            self.run_crawler_one_keys(id_experiment)
        else:
            self.run_crawler_four_keys(id_experiment)
    
    def get_seed_type(self,seed_name):
        app_id=configuration.APP_ID
        app_key=configuration.API_KEY_DANDELION
        datatxt = DataTXT(app_id=app_id, app_key=app_key)
        response = datatxt.nex(seed_name, **{"min_confidence":0.6,"include":["types"]})
        return response.annotations
    
    def get_all_seed_type(self,seeds):
        typed_seeds=[]
        for s in seeds:
            try:
                print(s["handle"])
                name=self.db_manager.get_seed_name(s["_id"])
                print(name)
                if(name==None):
                    continue
                types = self.get_seed_type(name)
                concrete_types = self.find_concrete_type(types["types"],self.ontology)
                types.update({
                    "concrete_types":concrete_types
                })
                self.db_manager.update("seeds",{"_id":s["_id"]},{"$set":{"annotations":types}})
            except DandelionException as e:
                print(e.message)
                continue

    

    def run_crawler_one_keys(self,id_experiment):
        self.id_experiment = id_experiment

        # Documentation: http://python-dandelion-eu.readthedocs.io/en/latest/datatxt.html#nex-named-entity-extraction
        languages = ("de", "en", "es", "fr", "it", "pt")

        all_tweets = list(self.db_manager.find("tweets", {"id_experiment":id_experiment}))

        tweets_each_request = math.ceil(len(all_tweets) / configuration.NUMBER_REQUEST_DANDELION)
        print(len(all_tweets), tweets_each_request)

        # Retrieve all tweets
        languages_chunks = []
        for l in languages:
            tweets = list(self.db_manager.find("tweets", {"lang": l, "id_experiment":id_experiment}))
            if (len(tweets) == 0):
                continue
            # print(l,len(tweets), len(tweets)%tweets_each_request)
            mod_tweets = tuple([tweets.pop() for i in range(0, len(tweets) % tweets_each_request)])
            # print(l,mod_tweets,len(tweets), len(tweets)%tweets_each_request)

            tweets_chunks = list(zip(*[iter(tweets)] * tweets_each_request))
            # print(len(tweets_chunks))
            if mod_tweets != ():
                tweets_chunks.append(mod_tweets)
            # print(len(tweets_chunks))

            languages_chunks.extend(tweets_chunks)

        self.run(languages_chunks, configuration.APP_ID, configuration.API_KEY_DANDELION)

    def run_crawler_four_keys(self,id_experiment):
        self.id_experiment = id_experiment

        # Documentation: http://python-dandelion-eu.readthedocs.io/en/latest/datatxt.html#nex-named-entity-extraction
        self.db_manager = mongo_manager.MongoManager(configuration.db_name)
        languages = ("de", "en", "es", "fr", "it", "pt")

        all_tweets = list(self.db_manager.find("tweets", {"id_experiment":id_experiment}))
        chunks_for_each_key = math.ceil(len(all_tweets) / 4)
        tweets_each_request = math.ceil(chunks_for_each_key / configuration.NUMBER_REQUEST_DANDELION)

        print(len(all_tweets), chunks_for_each_key, tweets_each_request)

        # Retrieve all tweets
        languages_chunks = []
        for l in languages:
            tweets = list(self.db_manager.find("tweets", {"lang": l, "id_experiment":id_experiment}))
            if (len(tweets) == 0):
                continue
            # print(l,len(tweets), len(tweets)%tweets_each_request)
            mod_tweets = tuple([tweets.pop() for i in range(0, len(tweets) % tweets_each_request)])
            # print(l,mod_tweets,len(tweets), len(tweets)%tweets_each_request)

            tweets_chunks = list(zip(*[iter(tweets)] * tweets_each_request))
            # print(len(tweets_chunks))
            if mod_tweets != ():
                tweets_chunks.append(mod_tweets)
            # print(len(tweets_chunks))

            languages_chunks.extend(tweets_chunks)

        self.split_tweets_and_run(languages_chunks)

    def split_tweets_and_run(self, tweets):
        size_chunk = math.ceil(len(tweets) / 4)

        # Run crawler with the 4 different Dandelion keys (Rate limit: 1000 req/day)
        self.run(tweets[:size_chunk], configuration.APP1_ID, configuration.API_KEY_DANDELION1)
        self.run(tweets[size_chunk:size_chunk * 2], configuration.APP2_ID, configuration.API_KEY_DANDELION2)
        self.run(tweets[size_chunk * 2:size_chunk * 3], configuration.APP3_ID, configuration.API_KEY_DANDELION3)
        self.run(tweets[size_chunk * 3:], configuration.APP4_ID, configuration.API_KEY_DANDELION4)
    
    def is_parent(self,node,parent,tree, found=False):
        result = None
        keys = tree.keys()

        if(node in keys):
            return found
        else:
            for k in keys:
                if(k==parent):
                    found=True
                result = self.is_parent(node,parent,tree[k],found)
                if(result):
                    return True
        
        return False
    
    def find_concrete_type(self,types,ontology):
        results = []
        for t in types:
            found = False
            for k in types:
                if(self.is_parent(k,t,ontology)):
                    found=True
                    break
            if(not found):
                results.append(t)
                
        return results

    def run(self, tweets_chunks, app_id, app_key):
        datatxt = DataTXT(app_id=app_id, app_key=app_key)
        for tweets in tweets_chunks:
            join_tweets = tweets_chunk.TweetsChunk(tweets)
            pprint.pprint(len(tweets))
            try:
                response = datatxt.nex(join_tweets.get_unique_string(), **{"lang": tweets[0]["lang"],
                                                                           "include": ["types", "categories",
                                                                                       "abstract", "alternate_labels"],
                                                                           "social.hashtag": True,
                                                                           "social.mention": True,
                                                                           "min_confidence":0})
                # print(response)
            except DandelionException as e:
                logging.error(e.code, e.message)
                continue
            join_tweets.split_annotation_each_tweet(response.annotations)
            # pprint.pprint(join_tweets.index_tweet)
            for tweet in join_tweets.index_tweet:
                    #seed_id = list(self.db_manager.find("seeds", {"handle": tweet["tweet"]["user"]["screen_name"], "id_experiment":self.id_experiment}))
                    #if(len(seed_id)>0):
                    #        seed_id=seed_id[0]["_id"]
                    #else:
                    #    pprint.pprint(tweet["tweet"]["user"]["screen_name"])
                    #    continue

                    seed_id = tweet["tweet"]["seed"]
                    for annotation in tweet["annotations"]:
                        annotation["tweet"] = tweet["tweet"]["_id"]
                        annotation["seed"] = seed_id
                        annotation["concrete_types"] = self.find_concrete_type(annotation["types"],self.ontology)
                        annotation["id_experiment"] = self.id_experiment
                        #print(annotation)
                        self.db_manager.write_mongo("entity", annotation)
