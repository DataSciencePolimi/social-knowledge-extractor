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
            consideredMention.append(entity["label"])
            #if "@" in entity["spot"] or "#" in entity["spot"]:

        entities.close()
        return consideredMention

   
    def __init__(self,db,expertTypes):
        self.db = db
        self.expertTypes = expertTypes
