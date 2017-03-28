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
from dandelion.cache.base import NoCache


class CrawlerTestPerformance(unittest.TestCase):

    def test_limit_rate(self):
        datatxt = DataTXT(app_id="7342eec6", app_key="76012ac4dc76150ae485bf553c69b127")
        response = datatxt.nex("RT @sickymagazine: 'Sisters Forever' by Viola Rolando for SICKY Magazine http://t.co/NpAGg6za09 @NextModels @Missoni @nikestore @LucaLarenz…", **{"lang": "en",
                                                                           "include": ["types", "categories",
                                                                                       "abstract", "alternate_labels"],
                                                                           "social.hashtag": True,
                                                                           "social.mention": True,
                                                                           "min_confidence":0})
        print(response)

    # def test_time_confidence(self):
    #     datatxt = DataTXT(app_id=configuration.APP1_ID, app_key=configuration.API_KEY_DANDELION1)
    #     #with confidence
    #     start_time = time.time()
    #     datatxt.nex("RT @sickymagazine: 'Sisters Forever' by Viola Rolando for SICKY Magazine http://t.co/NpAGg6za09 @NextModels @Missoni @nikestore @LucaLarenz…", **{"lang": "en",
    #                                                                        "include": ["types", "categories",
    #                                                                                    "abstract", "alternate_labels"],
    #                                                                        "social.hashtag": True,
    #                                                                        "social.mention": True,
    #                                                                        "min_confidence":0})
    #     print("--- %s seconds ---" % (time.time() - start_time))
    #
    #     #without confidence
    #     start_time = time.time()
    #     datatxt.nex("RT @sickymagazine: 'Sisters Forever' by Viola Rolando for SICKY Magazine http://t.co/NpAGg6za09 @NextModels @Missoni @nikestore @LucaLarenz…", **{"lang": "en",
    #                                                                        "include": ["types", "categories",
    #                                                                                    "abstract", "alternate_labels"],
    #                                                                        "social.hashtag": True,
    #                                                                        "social.mention": True})
    #     print("--- %s seconds ---" % (time.time() - start_time))


if __name__ == '__main__':
    unittest.main()

