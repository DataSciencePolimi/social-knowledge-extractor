class AST:
    
    def getEntities(self,seed):
        query = {
            "seed":seed["_id"]
        }

        mentions = []
        entities = self.db.getMentionType(query)

        for e in entities:
            mentions+=e["types"]

        return mentions
    
    def __init__(self,db,expertTypes):
        self.db = db