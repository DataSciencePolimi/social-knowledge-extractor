__author__ = 'marcotagliabue'

import unittest
import logging
import pprint
import random
import time

from dandelion import DataTXT

from utils import mongo_manager
import configuration
from crawler.crawler_dandelion import CrawlDandelion
from crawler.crawler_twitter import CrawlerTwitter


class CrawlerTest(unittest.TestCase):
    def setUp(self):
        self.db_manager = mongo_manager.MongoManager(configuration.db_name)
        self.db_manager_test = mongo_manager.MongoManager(configuration.db_name_test)
        self.db_manager_test.delete_many("tweets", {})
        self.db_manager_test.delete_many("seeds", {})

        self.num_tweet_for_test = 20

        # Extract n random tweet from list
        if len(list(self.db_manager_test.find("tweets", {}))) == 0:
            logging.info("Crawl exemples seeds...")
            crawler_twitter = CrawlerTwitter("12345")
            seeds = ["EleonoraM_37"]
            new_seeds = crawler_twitter.run(100, seeds)
            crawler_twitter.run(100, new_seeds)
            crawler_twitter.storeSeeds(seeds)

        tweets_test = random.sample(list(self.db_manager.find("tweets", {"id_experiment":"12345"})), self.num_tweet_for_test)
        print(tweets_test)
        self.db_manager_test.write_mongo("tweets", tweets_test)
        for t in tweets_test:
            pprint.pprint(t["user"]["screen_name"])
            seed_test = list(self.db_manager.find("seeds", {"handle": t["user"]["screen_name"],"id_experiment":"12345" }))
            self.db_manager_test.write_mongo("seeds", seed_test)

        configuration.db_name = configuration.db_name_test

    def test_crawler(self):
        CrawlDandelion("12345", False)



if __name__ == '__main__':
    unittest.main()
