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
       
    def __init__(self,dbmane):    
        self.client = MongoClient()
        self.db = self.client[dbmane]
