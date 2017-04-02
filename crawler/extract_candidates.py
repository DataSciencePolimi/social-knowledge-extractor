__author__ = 'marcotagliabue'
"""
 Decription: This script computes the tf and df score for the set of handles that are mentioned by, or
 appear together with the seeds. The script is meant to be executed against a database that has, at the
 very least, three collections: seeds, entities, and lfentities. The output of the script is an array
 with the 250 handles with the highest tf·df score.
 Author: Marco Tagliabue
 Date: 2017-02-27

"""
import pymongo
from ttp import ttp

from utils import mongo_manager
import configuration


class ExtractCandidates:
    def __init__(self, id_experiment):
        self.id_experiment = id_experiment
        self.db_manager = mongo_manager.MongoManager(configuration.db_name)
        self.parse_text = ttp.Parser()


    def computeDF(self, candidate, seeds):
        # Number of seeds with which a candidate co-occurs with
        # Query MongoDB db.getCollection('tweets').find({"$and":[{"entities.user_mentions.screen_name":"gucci"},{"entities.user_mentions.screen_name":"GalGadot"}]},{"entities.user_mentions.screen_name":1})
        # Return all elements with at least 2 user mentions: db.getCollection('tweets').find({"entities.user_mentions.1": {$exists: true}})
        co_occurences = list(self.db_manager.aggregate("tweets",[{"$project":{"entities.user_mentions.screen_name":1}},{"$match":{"entities.user_mentions.screen_name":candidate["handle"], "id_experiment":self.id_experiment}}, {"$unwind" : "$entities.user_mentions"}]))
        candidates_mentions = set([f["entities"]["user_mentions"]["screen_name"] for f in co_occurences])
        DF = len(candidates_mentions.intersection(set(seeds)))
        return DF

    def computeTTF(self, candidate):
        occurences = list(self.db_manager.find("entity_lf", {"spot": candidate["handle"], "category": "mention", "id_experiment":self.id_experiment}))
        return len(occurences)

    def get_candidates_lf(self, candidates):
        #print(len(candidates))
        hig_frequencies = list(self.db_manager.find("entity", {"spot": {"$regex" : "@"}, "id_experiment":self.id_experiment}))

        hf = []
        for t in hig_frequencies:
            handles = self.parse_text.parse(t["spot"]).users
            if handles:
                hf.append(handles[0].lower())

        #print(len(set(hf)))
        #print(hf)
        #print([c["handle"] for c in candidates])
        return [c for c in candidates if c["handle"].lower() not in set(hf)]


    def extract_candidates(self):

        # Number of seeds
        seeds = [s["handle"] for s in list(self.db_manager.find("seeds", {"starting": True,"id_experiment":self.id_experiment}))]
        N = len(seeds)

        candidates = list(self.db_manager.find("seeds", {"starting": False, "id_experiment":self.id_experiment}))
        #low_candidates = self.get_candidates_lf(candidates)

        rank = candidates.copy()
        i = 0
        for ca in rank:
            DF = self.computeDF(ca, seeds)
            i+=1
            #print(i)
            TTF = self.computeTTF(ca)
            formula = (DF * TTF) / (N - DF + 1)
            ca["ranking_index"] = formula

        for item in rank:
            item.update( {"id_experiment":self.id_experiment})
        self.db_manager.write_mongo("rank_candidates", rank)
        return list(self.db_manager.find("rank_candidates", {"id_experiment":self.id_experiment}).sort("ranking_index", pymongo.DESCENDING))[:250]


if __name__ == "__main__":
    e = ExtractCandidates("12345")
    e.extract_candidates()
