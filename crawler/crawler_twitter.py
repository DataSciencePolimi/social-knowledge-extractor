__author__ = 'marcotagliabue'

from utils import mongo_manager
from crawler.crawler_user_timeline import CrawlerUserTimelineTwitter
import configuration
from pymongo import IndexModel, DESCENDING
from pydash import py_
import pprint

class CrawlerTwitter():
    def __init__(self, id_experiment,db_manager):
        self.id_experiment = id_experiment
        self.db_manager = db_manager

        self.tokens = self.db_manager.get_user_twitter_tokens(id_experiment)
        self.crawler = CrawlerUserTimelineTwitter(self.tokens)
        #self.db_manager.create_index("tweets", [("id_str", DESCENDING),("id_experiment", DESCENDING)])
        #self.db_manager.create_index("seeds",[("handle", DESCENDING),("id_experiment", DESCENDING)])

    def storeSeeds(self, original_seeds):
        initial_seeds = [s["handle"] for s in original_seeds]
        storable = []
        for t in self.db_manager.find("tweets", {"id_experiment":self.id_experiment}):
            storable.append(t["user"]["screen_name"])

        for t in set(storable):
            if t in initial_seeds:
                self.db_manager.write_mongo("seeds", {"handle": t, "starting": True, "types":original_seeds[initial_seeds.index(t)]["types"], "id_experiment":self.id_experiment})
            else:
                self.db_manager.write_mongo("seeds", {"handle": t, "starting": False, "id_experiment":self.id_experiment})

    def run(self, N, seeds):
        new_seeds = []
        # Exctract all the tweets
        for s in seeds:
            print("Starting seed: "+s["handle"])
            tweets_seed = self.crawler.get_users_tweets(s["handle"], N)
            if (len(tweets_seed) == 0):
                self.db_manager.delete_element("seeds", {"handle": s["handle"],"id_experiment":self.id_experiment})
                continue
            # else:
            #     logging.info(s+" Tweets' number: "+str(len(tweets_seed)))

            for item in tweets_seed:
                item.update( {"id_experiment":self.id_experiment})

            self.db_manager.write_mongo("tweets", tweets_seed)

            handels_new = set(self.crawler.get_all_handles_mentioned(tweets_seed, s["handle"]))
            # print(s+" Handles mentioned: "+" ".join(handels_new))

            handles = []
            for h in handels_new:
                h_dict = {
                    "handle":h,
                    "origin":s["handle"]
                }
                new_seeds.append(h_dict)

            #if len(handles) != 0:
                # self.db_manager.write_mongo("seeds", [{"handle":h, "starting":False} for h in handels_new])
                #pprint.pprint(handles)
                #new_seeds = list(set(new_seeds+handles))
        
        new_seeds = py_(new_seeds).group_by("handle").to_pairs().map(lambda p: {"handle":p[0],"origin":py_.map(p[1],"origin")}).value()
        return new_seeds
