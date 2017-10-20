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
import pprint

class PipelineCrawler:

    def run(self, one_dandelion_key = True):
        print("Pipeline started!")
        print("Seeds: ", len(self.seeds), self.seeds)
        print("Hubs: ", len(self.hubs), self.hubs)

        # Crawling Tweet
        print("Crawling Twitter...")
        crawler_twitter = CrawlerTwitter(self.id_experiment,self.db_manager)
        
        print("Crawling first seeds or hub")
        new_seeds = crawler_twitter.run(self.N, self.original_seeds)
        # I need the mongo id
        new_seeds = self.db_manager.get_unranked_candidates(self.id_experiment)

        if(self.isHub):
            print("Crawling the seeds")
            crawler_twitter.run(self.N,self.seeds)
        

        print("Crawling the mentions")
        crawler_twitter.run(self.N, new_seeds)
        #crawler_twitter.storeSeeds(self.original_seeds)

        # Extract Low Frequencies Entities
        #print("Extract Mention and Hashtag from Tweets...")
        #ExtractEntities(self.id_experiment)

        # Compute ranking candidates
        print("Compute DF/TFF and rank candidates...")
        ExtractCandidates(self.id_experiment).extract_candidates()

        #Email sender with rank is needed
        #print(list(self.db_manager.find("rank_candidates", {}).sort("ranking_index", pymongo.DESCENDING))[:250])

    def __init__(self, N, id_experiment,db_manager,isHub):
        self.db_manager = db_manager
        self.N = N

        query = {
            "id_experiment":id_experiment
        }

        self.isHub = isHub
        self.seeds = self.db_manager.getSeeds(query)   
        self.hubs = self.db_manager.getHubs(query)
        
        if(isHub):
            self.original_seeds = self.hubs
        else:  
            self.original_seeds = self.seeds
        
        self.id_experiment = id_experiment
       

if __name__ == "__main__":
