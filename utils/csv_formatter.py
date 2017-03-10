__author__ = 'marcotagliabue'

"""
Description:
    Formatting Datasets stored in MongoDb following theese rules:
    - seed_au_old.csv: file containing the initial seed in the form of (id,name) where id is the id in the database
    - cand.csv: file containing the candidates in the form of (id,name) where id is the id in the database
    - seed_entities.csv: file containing the entities mentioned by the seed. It has the format id, seed (as db id), tweet (as db id), spot (the word in the tweet), type (dbpedia type corresponding to the mention), confidence
    - seed_lfentities.csv: file containing the low frequence entity mentioned by the seed. It has the format id, seed (as db id), tweet (as db id), spot (the word in the tweet), categories (type of mention, hashtag, @...)
    - cand_entities.csv: same as seed
    - cand_lfentities.csv: same as seed
    - expert_type.csv: file containing the type we are interested to discover (?)
    - dbpedia_type: file containing the high frequency type with format (name, level)
Date: 2017-02-27
"""

import pandas as pd
import pymongo

from utils import mongo_manager
import configuration


class CsvFormatter:
    def __init__(self):
        self.db_manager = mongo_manager.MongoManager(configuration.db_name)

        seeds = list(self.db_manager.find("seeds", {"starting": True}))
        seed_ids = [s["_id"] for s in seeds]
        candidates = list(self.db_manager.find("rank_candidates", {}).sort("ranking_index", pymongo.DESCENDING))[:250]
        cand_ids = [c["_id"] for c in candidates if (c["ranking_index"] != 0)]

        self.seed_candidates_to_csv(seeds, "../data/Out_csv/seed.csv")
        self.seed_candidates_to_csv(candidates, "../data/Out_csv/cand.csv")

        entities_lf_seed = list(self.db_manager.find("entity_lf", {"seed": {"$in": seed_ids}}))
        self.save_entities_lf(entities_lf_seed, "../data/Out_csv/seed_lfentities.csv")
        entities_lf_cand = list(self.db_manager.find("entity_lf", {"seed": {"$in": cand_ids}}))
        self.save_entities_lf(entities_lf_cand, "../data/Out_csv/cand_lfentities.csv")

        entities_seed = list(self.db_manager.find("entity", {"seed": {"$in": seed_ids}}))
        self.save_entities(entities_seed, "../data/Out_csv/seed_entities.csv")
        entities_cand = list(self.db_manager.find("entity", {"seed": {"$in": cand_ids}}))
        self.save_entities(entities_cand, "../data/Out_csv/cand_entities.csv")

    def seed_candidates_to_csv(self, items, path):
        rows = []
        for item in items:
            rows.append({"seed_id": item["_id"], "seed_name": item["handle"]})

        data_frame = pd.DataFrame(rows)
        data_frame[["seed_id", "seed_name"]].to_csv(path, header=True, index=False)

    def save_entities_lf(self, entities, path):
        rows = []
        for item in entities:
            rows.append({"_id": item["_id"], "seed": item["seed"], "tweet": item["tweet"], "spot": item["spot"],
                         "categories": item["category"]})

        data_frame = pd.DataFrame(rows)
        data_frame[["_id", "seed", "tweet", "spot", "categories"]].to_csv(path, header=True, index=False)

    def save_entities(self, entities, path):
        rows = []
        for item in entities:
            for c in item["types"]:
                rows.append({"_id": item["_id"], "seed": item["seed"], "tweet": item["tweet"], "spot": item["spot"],
                             "type": c.replace("http://dbpedia.org/ontology/", ""), "confidence": item["confidence"]})

        data_frame = pd.DataFrame(rows)
        data_frame[["_id", "seed", "tweet", "spot", "type", "confidence"]].to_csv(path, header=True, index=False)


if __name__ == "__main__":
    c = CsvFormatter()
