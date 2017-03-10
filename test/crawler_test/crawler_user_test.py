__author__ = 'marcotagliabue'

import unittest
from crawler import crawler_user_timeline


class CrawlerTest(unittest.TestCase):
    def setUp(self):
        self.c = crawler_user_timeline.CrawlerUserTimelineTwitter()
        # user with no tweets
        self.user_no_tweets = "ElleGermany"
        # user with a lot of tweets
        self.user_lots_tweets = "MarcoBrambi"
        # user with few of tweets
        self.user_few_tweets = "marcotagliabue"
        # suspended user
        self.user_suspeded = "fedebrighi"
        # user doesn't exist
        self.user_suspeded = "IamLilZaTweets"

    def test_crawler(self):
        N = 100
        print(self.user_suspeded)
        print(self.c.get_users_tweets(self.user_suspeded, N))
        self.assertEqual([], self.c.get_users_tweets(self.user_suspeded, 100))

        # test suspended account
        N = 100
        print(self.user_suspeded)
        self.assertEqual([], self.c.get_users_tweets(self.user_suspeded, N))

        # Twitter pagination is 200 tweet per request: test less tweet
        N = 100
        print(self.user_lots_tweets)
        self.assertEqual(N, len(self.c.get_users_tweets(self.user_lots_tweets, N)))

        # Twitter pagination is 200 tweet per request: test exactly 200 tweet
        N = 200
        print(self.user_lots_tweets)
        self.assertEqual(N, len(self.c.get_users_tweets(self.user_lots_tweets, N)))

        # Twitter pagination is 200 tweet per request: test user with no tweets
        N = 100
        print(self.user_no_tweets)
        self.assertEqual([], self.c.get_users_tweets(self.user_no_tweets, N))

        N = 100
        print(self.user_few_tweets)
        print(len(self.c.get_users_tweets(self.user_few_tweets, N)))
        self.assertLess(len(self.c.get_users_tweets(self.user_few_tweets, N)), N)


if __name__ == '__main__':
    unittest.main()
