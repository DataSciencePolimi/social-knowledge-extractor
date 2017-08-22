import json
import pprint
import mongo_manager
from bson.objectid import ObjectId

import configuration

db_manager = mongo_manager.MongoManager(configuration.db_name)

tweets = list(db_manager.db["tweets"].find({"id_experiment":ObjectId("59662c9dd57606bab977a612")}))

cooccurences = []
print(len(tweets))
for t in tweets:
    user_mentions = t["entities"]["user_mentions"]
    if(len(user_mentions)<2):
        continue
    handles = list(map(lambda x: x["screen_name"],user_mentions))
    cooccurences.append(handles)

pprint.pprint(cooccurences[0])