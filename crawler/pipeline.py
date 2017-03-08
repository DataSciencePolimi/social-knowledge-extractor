__author__ = 'marcotagliabue'

import pandas as pd
from Services import csv_formatter
from extract_entites import ExtractEntities
from extract_candidates import ExtractCandidates
from crawler_dandelion import CrawlDandelion
from crawler_twitter import CrawlerTwitter


class Pipeline:
    def __init__(self, N, seeds):
        print("Pipeline started!")
        print("Seeds: ", seeds)

        # Crawling Tweet
        print("Crawling Twitter...")
        crawler_twitter = CrawlerTwitter()
        new_seeds = crawler_twitter.run(N, seeds)
        crawler_twitter.run(N, new_seeds)
        crawler_twitter.storeSeeds(seeds)

        # Crawling Dandelion
        print("Crawling Dandelion for High Frequencies Entities...")
        CrawlDandelion()

        # Extract Low Frequencies Entities
        print("Extract Mention and Hashtag from Tweets...")
        ExtractEntities()

        # Compute ranking candidates
        print("Compute DF/TFF and rank candidates...")
        ExtractCandidates().extract_candidates()

        # Format results in CSV
        print("Compute DF/TFF and rank candidates...")
        csv_formatter.CsvFormatter()


if __name__ == "__main__":
    # Input seeds
    seeds_dataframe = pd.read_csv("Data/In_csv/seed_expo_old.csv")
    seeds = seeds_dataframe.ix[:, 1].tolist()
    print(seeds)
    Pipeline(100, seeds) #Starting time 15:24
