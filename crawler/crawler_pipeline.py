__author__ = 'marcotagliabue'

import pandas as pd
from utils import csv_formatter
from crawler.extract_entites import ExtractEntities
from crawler.extract_candidates import ExtractCandidates
from crawler.crawler_dandelion import CrawlDandelion
from crawler.crawler_twitter import CrawlerTwitter
import pymongo
from utils import mongo_manager
import configuration
from bson import ObjectId

class PipelineCrawler:

    def run(self, one_dandelion_key = True):
        print("Pipeline started!")
        print("Seeds: ", len(self.seeds), self.seeds)

        # Crawling Tweet
        print("Crawling Twitter...")
        crawler_twitter = CrawlerTwitter(self.id_experiment)
        new_seeds = crawler_twitter.run(self.N, self.seeds)
        crawler_twitter.run(self.N, new_seeds)
        crawler_twitter.storeSeeds(self.original_seeds)

        # Crawling Dandelion
        print("Crawling Dandelion for High Frequencies Entities...")
        CrawlDandelion(self.id_experiment, one_dandelion_key)

        # Extract Low Frequencies Entities
        print("Extract Mention and Hashtag from Tweets...")
        ExtractEntities(self.id_experiment)

        # Compute ranking candidates
        print("Compute DF/TFF and rank candidates...")
        ExtractCandidates(self.id_experiment).extract_candidates()

        #Email sender with rank is needed
        #print(list(self.db_manager.find("rank_candidates", {}).sort("ranking_index", pymongo.DESCENDING))[:250])

    def __init__(self, N, seeds, id_experiment,db_manager):
        self.db_manager = db_manager
        self.N = N
        self.seeds = [s["handle"] for s in seeds]
        self.original_seeds = seeds
        self.id_experiment = id_experiment
       

# if __name__ == "__main__":
#     # Input seeds
#     seeds_dataframe = pd.read_csv("../data/In_csv/fashion/seed.csv")
#     seeds = seeds_dataframe.ix[:, 0].tolist()[:20]
#
#     #Add DbPedia Types to seeds and checks dandelion rate limit
#     from model import tweets_chunk
#     from utils import dandelion_interface
#     new_seeds = []
#     join_seeds = tweets_chunk.TweetsChunk([{"text":s} for s in seeds])
#     datatxt = dandelion_interface.EntityExtraction(app_id="7342eec6", app_key="76012ac4dc76150ae485bf553c69b127")
#     res = datatxt.nex(join_seeds.get_unique_string(), **{"include": ["types", "categories",
#                                                                         "abstract", "alternate_labels"],
#                                                                            "social.hashtag": True,
#                                                                            "social.mention": True,
#                                                                            "min_confidence":0})
#     join_seeds.split_annotation_each_tweet(res["annotations"])
#     for tweet in join_seeds.index_tweet:
#         ann = tweet.get("annotations",[])
#         if len(ann) != 0:
#             new_seeds.append({"handle":tweet["tweet"]["text"], "types":ann[0].get("types",[])})
#         else:
#             new_seeds.append({"handle":tweet["tweet"]["text"], "types":[]})
#     print(new_seeds)
#
#
#     p = PipelineCrawler(100, new_seeds, "12345", True) #Starting time 15:24
#     p.run()