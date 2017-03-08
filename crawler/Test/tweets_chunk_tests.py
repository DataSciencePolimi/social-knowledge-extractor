__author__ = 'marcotagliabue'

import unittest
from dandelion import DataTXT
from Services import mongo_manager
import configuration
from Model import tweets_chunk


class ChunksTest(unittest.TestCase):
    def setUp(self):
        # Retrieve all tweets
        tweets = list(mongo_manager.MongoManager(configuration.db_name).find("tweets", {}))[10:16]
        self.datatxt = DataTXT(app_id=configuration.APP1_ID, app_key=configuration.API_KEY_DANDELION1)
        self.t = tweets_chunk.TweetsChunk(tweets)

    def test_chunks(self):
        unique = self.t.get_unique_string()
        print(unique)
        response = self.datatxt.nex(self.t.get_unique_string(),
                                    **{"include": ["types", "categories", "abstract", "alternate_labels"],
                                       "social.hashtag": True, "social.mention": True})
        print(response.annotations)
        self.t.split_annotation_each_tweet(response.annotations)
        print(self.t.index_tweet)


if __name__ == '__main__':
    unittest.main()
