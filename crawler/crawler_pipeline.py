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
import yagmail

class PipelineCrawler:
    def __init__(self, N, seeds, id_experiment):
        self.db_manager = mongo_manager.MongoManager(configuration.db_name)

        print("Pipeline started!")
        print("Seeds: ", len(seeds), seeds)

        # Crawling Tweet
        print("Crawling Twitter...")
        crawler_twitter = CrawlerTwitter(id_experiment)
        new_seeds = crawler_twitter.run(N, seeds)
        crawler_twitter.run(N, new_seeds)
        crawler_twitter.storeSeeds(seeds)

        # Crawling Dandelion
        print("Crawling Dandelion for High Frequencies Entities...")
        CrawlDandelion(id_experiment)

        # Extract Low Frequencies Entities
        print("Extract Mention and Hashtag from Tweets...")
        ExtractEntities(id_experiment)

        # Compute ranking candidates
        print("Compute DF/TFF and rank candidates...")
        ExtractCandidates(id_experiment).extract_candidates()

        # Format results in CSV
        #print("Compute DF/TFF and rank candidates...")
        #csv_formatter.CsvFormatter()

        #Update status of requested Pipeline
        user = list(self.db_manager.find("experiment",{"_id":id_experiment}))[0]
        user["status"] = "complete"
        self.db_manager.update("experiment",{"_id":id_experiment}, user)

        #Email sender with rank is needed
        print(list(self.db_manager.find("rank_candidates", {}).sort("ranking_index", pymongo.DESCENDING))[:250])

if __name__ == "__main__":
    # Input seeds
    seeds_dataframe = pd.read_csv("../data/In_csv/seed_expo_old.csv")
    seeds = seeds_dataframe.ix[:, 1].tolist()
    print(seeds)
    PipelineCrawler(100, seeds, "12345") #Starting time 15:24
