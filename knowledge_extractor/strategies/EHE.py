import pprint
class EHE:
    
    def getEntities(self,seed):
        # need to select onlu the expert type entity

        query = {
            "types":{
                "$in":self.expertTypes
            },
            "seed":seed["_id"]
        }

        entities = self.db.getMentions(query)

        consideredMention = []
        for entity in entities:
            if entity["spot"].startswith("@") or entity["spot"].startswith("#"):
               consideredMention.append(entity["label"])

        return consideredMention

   
    def __init__(self,db,expertTypes):
        self.db = db
        self.expertTypes = expertTypes
