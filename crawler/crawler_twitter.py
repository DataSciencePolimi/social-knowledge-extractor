__author__ = 'marcotagliabue'

from Services import mongo_manager
import crawler_user_timeline
import configuration

class CrawlerTwitter():
    def __init__(self):
        self.crawler = crawler_user_timeline.CrawlerUserTimelineTwitter()
        self.db_manager = mongo_manager.MongoManager(configuration.db_name)
        self.db_manager.create_index("tweets", "id_str")
        self.db_manager.delete_many("tweets", {})
        self.db_manager.create_index("seeds", "handle")
        self.db_manager.delete_many("seeds", {})

    def storeSeeds(self, initial_seeds):
        storable = []
        for t in self.db_manager.find("tweets", {}):
            storable.append(t["user"]["screen_name"])

        for t in set(storable):
            if t in initial_seeds:
                self.db_manager.write_mongo("seeds", {"handle": t, "starting": True})
            else:
                self.db_manager.write_mongo("seeds", {"handle": t, "starting": False})

    def run(self, N, seeds):
        new_seeds = []
        # Exctract all the tweets
        for s in seeds:
            # print("Starting seed: "+s)
            tweets_seed = self.crawler.get_users_tweets(s, N)
            if (len(tweets_seed) == 0):
                self.db_manager.delete_element("seeds", {"handle": s})
                continue
            # else:
            #     logging.info(s+" Tweets' number: "+str(len(tweets_seed)))

            self.db_manager.write_mongo("tweets", tweets_seed)

            handels_new = set(self.crawler.get_all_handles_mentioned(tweets_seed, s))
            # print(s+" Handles mentioned: "+" ".join(handels_new))

            if len(handels_new) != 0:
                # self.db_manager.write_mongo("seeds", [{"handle":h, "starting":False} for h in handels_new])
                new_seeds.extend(handels_new)

        return new_seeds
