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

     def get_all_handles_mentioned(self, list_of_tweet, owner):

        mentions = []
        for tweet in list_of_tweet:
            mentions.extend([mention["screen_name"] for mention in tweet["entities"]["user_mentions"]])

        mentions_unique = list(set(mentions))

        if owner in mentions_unique:
            mentions_unique.remove(owner)

        return mentions_unique

    def run(self, N, seeds):
        new_seeds = []
        # Exctract all the tweets
        for s in seeds:
            print("Starting seed: "+s["handle"])
            tweets_seed = self.db_manager.getTweets(s["handle"], self.id_experiment)
            if (len(tweets_seed) == 0):
                continue
                        

            handels_new = set(self.get_all_handles_mentioned(tweets_seed, s["handle"]))
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
