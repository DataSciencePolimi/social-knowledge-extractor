__author__ = 'marcotagliabue'

class TweetsChunk:
    def __init__(self, tweets):
        self.tweets = tweets

    def get_unique_string(self):
        # Join tweets in  a unique tweet and save starting and ending indexes of each of them
        self.index_tweet = []
        start = 0
        for t in self.tweets:
            self.index_tweet.append({"tweet": t, "start": start, "end": start + len(t["text"]) - 1, "annotations": []})
            start = start + len(t["text"]) + 1

        return " ".join([t["text"].replace("\n", " ") for t in self.tweets])

    def split_annotation_each_tweet(self, annotations):
        for t in self.index_tweet:
            for a in annotations:
                if (a['start'] >= t["start"] and a["end"] <= t["end"]):
                    t["annotations"].append(a)


if __name__ == "__main__":
    t = TweetsChunk([{"text": "Lorem ipsum dolor sit amet"}, {"text": "Nullam dictum felis eu pede mollis pretium"},
                     {"text": "dolor sit amet"}])
    print(t.get_unique_string())
    print(t.index_tweet)
