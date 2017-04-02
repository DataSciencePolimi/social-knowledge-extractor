__author__ = 'marcotagliabue'

from utils import mongo_manager
from crawler.crawler_user_timeline import CrawlerUserTimelineTwitter
import configuration
from pymongo import IndexModel, DESCENDING

class CrawlerTwitter():
    def __init__(self, id_experiment):
        self.id_experiment = id_experiment
        self.crawler = CrawlerUserTimelineTwitter()
        self.db_manager = mongo_manager.MongoManager(configuration.db_name)

        self.db_manager.create_index("tweets", [("id_str", DESCENDING),("id_experiment", DESCENDING)])
        self.db_manager.create_index("seeds",[("handle", DESCENDING),("id_experiment", DESCENDING)])

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
        new_seeds = set()
        # Exctract all the tweets
        for s in seeds:
            print("Starting seed: "+s)
            tweets_seed = self.crawler.get_users_tweets(s, N)
            if (len(tweets_seed) == 0):
                self.db_manager.delete_element("seeds", {"handle": s,"id_experiment":self.id_experiment})
                continue
            # else:
            #     logging.info(s+" Tweets' number: "+str(len(tweets_seed)))

            for item in tweets_seed:
                item.update( {"id_experiment":self.id_experiment})
            self.db_manager.write_mongo("tweets", tweets_seed)

            handels_new = set(self.crawler.get_all_handles_mentioned(tweets_seed, s))
            # print(s+" Handles mentioned: "+" ".join(handels_new))

            if len(handels_new) != 0:
                # self.db_manager.write_mongo("seeds", [{"handle":h, "starting":False} for h in handels_new])
                new_seeds.update(handels_new)

        return new_seeds
