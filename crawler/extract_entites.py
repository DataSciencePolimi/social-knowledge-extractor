__author__ = 'marcotagliabue'
from utils import mongo_manager
import configuration
from bson import ObjectId
from pymongo import IndexModel, DESCENDING

class ExtractEntities():
    def __init__(self, id_experiment):

        self.id_experiment = id_experiment
        self.db_manager = mongo_manager.MongoManager(configuration.db_name)
        self.db_manager.create_index("seed_candidates", [("id_candidate", DESCENDING),("id_experiment", DESCENDING)])

        tweets = list(self.db_manager.find("tweets", {"id_experiment":id_experiment}))
        self.run(tweets)

    def save_seed_mention(self, seed, user_mentions):
        for men in user_mentions:
            men = list(self.db_manager.find("seeds", {"handle":men["screen_name"],"starting":False}))
            if len(men) != 0:
                self.db_manager.write_mongo("seed_candidates",{"id_seed":seed, "id_candidate":men[0]["_id"],"id_experiment":self.id_experiment})

    def run(self, tweets):
        for tw in tweets:
            # print("Tweet: ",tw)
            hashtags = tw["entities"]["hashtags"]
            mentions = tw["entities"]["user_mentions"]
            # print(tw["user"]["screen_name"])
            #seed_id = list(self.db_manager.find("seeds", {"handle": tw["user"]["screen_name"], "id_experiment":self.id_experiment}))[0]["_id"]
            seed_id = tw["seed"]

            for h in hashtags:
                # print({"tweet":tw["id"], "seed":seed_id, "spot":h["text"], "category": "hashtag"})
                self.db_manager.write_mongo("entity_lf", {"tweet": tw["_id"], "seed": seed_id, "spot": h["text"],
                                                          "category": "hashtag", "id_experiment":self.id_experiment})

            for m in mentions:
                # print({"tweet":tw["id"], "seed":seed_id, "spot":m["screen_name"], "category": "mention"})
                self.db_manager.write_mongo("entity_lf", {"tweet": tw["_id"], "seed": seed_id, "spot": m["screen_name"],
                                                          "category": "mention", "id_experiment":self.id_experiment})

            self.save_seed_mention(seed_id,mentions)


if __name__ == "__main__":
    e = ExtractEntities(ObjectId("58c7fb3968f62013c2b5b060"))
