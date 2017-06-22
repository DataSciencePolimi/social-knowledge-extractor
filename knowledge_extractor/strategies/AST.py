import pprint

class AST:
    
    def getEntities(self,seed):
        query = {
            "seed":seed["_id"]
        }

        mentions = []
        entities = self.db.getMentionType(query)

        for e in entities:
            mentions+=e["types"]
        
        entities.close()

        return mentions
    
    def getAllEntities(self,id_experiment):
        query = [{"$match":{"id_experiment":id_experiment,"types":{"$not":{"$size":0}}}},{"$project":{"seed":1,"types":1}},{"$unwind":"$types"},{"$group":{"_id":"$seed","type":{"$push":"$types"}}}]
    
    def __init__(self,db,expertTypes):
        self.db = db