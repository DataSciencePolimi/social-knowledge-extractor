__author__ = 'marcotagliabue'
from Services import mongo_manager
import configuration


class ExtractEntities():
    def __init__(self):
        self.db_manager = mongo_manager.MongoManager(configuration.db_name)
        self.db_manager.delete_many("entity_lf", {})

        tweets = list(self.db_manager.find("tweets", {}))
        self.run(tweets)

    def run(self, tweets):
        for tw in tweets:
            # print("Tweet: ",tw)
            hashtags = tw["entities"]["hashtags"]
            mentions = tw["entities"]["user_mentions"]
            # print(tw["user"]["screen_name"])
            seed_id = list(self.db_manager.find("seeds", {"handle": tw["user"]["screen_name"]}))[0]["_id"]

            for h in hashtags:
                # print({"tweet":tw["id"], "seed":seed_id, "spot":h["text"], "category": "hashtag"})
                self.db_manager.write_mongo("entity_lf", {"tweet": tw["_id"], "seed": seed_id, "spot": h["text"],
                                                          "category": "hashtag"})

            for m in mentions:
                # print({"tweet":tw["id"], "seed":seed_id, "spot":m["screen_name"], "category": "mention"})
                self.db_manager.write_mongo("entity_lf", {"tweet": tw["_id"], "seed": seed_id, "spot": m["screen_name"],
                                                          "category": "mention"})


if __name__ == "__main__":
    e = ExtractEntities()
