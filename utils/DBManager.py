from pymongo import MongoClient

class DBManager:
    
    def getSeeds(self,query):
        collection = "seeds"
        return self.db[collection].find(query)

    def getCandidates(self,query):
        collection = "rank_candidates"
        return self.db[collection].find(query)

    def getMentions(self,query):
        collection = "entity"
        return self.db[collection].find(query,{"spot":1,"types":1,"label":1})
    
    def getMentionType(self,query):
        collection = "entity"
        return self.db[collection].find(query,{"types":1})

    def saveScores(self,scores):
        collection = "rankings"

        for k,v in scores.items():
            score = {
                "handle":k,
                "score":v,
                "experiment_id":self.experiment_id
            }
            self.db[collection].insert(score)
        
       
    def __init__(self,dbmane,experiment_id):    
        self.client = MongoClient()
        self.db = self.client[dbmane]
        self.experiment_id = experiment_id
