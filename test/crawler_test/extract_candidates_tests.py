__author__ = 'marcotagliabue'

import unittest

from crawler.extract_candidates import ExtractCandidates
from utils import mongo_manager
import configuration


class ExtractCandidatesTests(unittest.TestCase):
    # ['MauroGasperi1', 'Greta_Boldini', 'di_morabito', 'EleonoraM_37', 'LVCHINO_', 'LGReyewear', 'guendany', 'AquilanoRimondi', 'iuter', 'UelCamilo']
    # {'starting': False, '_id': ObjectId('58b439d5be48367e0e00e82a'), 'handle': 'enricomatzeu'} ['enricomatzeu', 'di_morabito']
    # ['MauroGasperi1', 'Greta_Boldini', 'di_morabito', 'EleonoraM_37', 'LVCHINO_', 'LGReyewear', 'guendany', 'AquilanoRimondi', 'iuter', 'UelCamilo']
    # {'starting': False, '_id': ObjectId('58b439d5be48367e0e00e82d'), 'handle': 'MDAsmeraldo'} ['MDAsmeraldo', 'LVCHINO_']

    def setUp(self):
        self.db_manager_test = mongo_manager.MongoManager(configuration.db_name_test)
        self.db_manager_test.delete_many("tweets", {})
        self.db_manager_test.write_mongo("tweets", {"entities":{"user_mentions":[{"screen_name":"marco"},{"screen_name":"luca"},{"screen_name":"andrea"}]}})
        self.db_manager_test.write_mongo("tweets", {"entities":{"user_mentions":[{"screen_name":"marco"}]}})
        self.db_manager_test.write_mongo("tweets", {"entities":{"user_mentions":[{"screen_name":"marco"},{"screen_name":"andrea"}]}})
        self.db_manager_test.write_mongo("tweets", {"entities":{"user_mentions":[{"screen_name":"marco"},{"screen_name":"luca"}]}})
        self.db_manager_test.write_mongo("tweets", {"entities":{"user_mentions":[{"screen_name":"luca"},{"screen_name":"andrea"}]}})
        self.db_manager_test.write_mongo("tweets", {"entities":{"user_mentions":[{"screen_name":"marco"},{"screen_name":"franco"}]}})

        self.seeds = ["luca", "andrea", "franco"]
        configuration.db_name = configuration.db_name_test
        self.e = ExtractCandidates()

    def test_chunks(self):
        self.assertEqual(3, self.e.computeDF({"handle":"marco"}, self.seeds))


if __name__ == '__main__':
    unittest.main()
