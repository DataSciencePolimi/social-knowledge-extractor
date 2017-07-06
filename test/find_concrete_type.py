import json
import pprint
import mongo_manager

import configuration

ontology_file = open('../data/dbpedia_ontology.json')
ontology_content = ontology_file.read()
ontology = json.loads(ontology_content)["owl:Thing"]

types = [
    "Person", 
    "Agent", 
    "President", 
    "Politician", 
    "OfficeHolder"
    ]


def go_to_node(node,tree):
    result = None
    keys = tree.keys()

    if(node in keys):
        return tree[node]
    else:
        for k in keys:
            result = go_to_node(node,tree[k])
            if(result!=None):
                return result
    
    return result

def is_parent3(node,parent,tree, found=False):
    result = None
    keys = tree.keys()

    if(node in keys):
        return found
    else:
        for k in keys:
            if(k==parent):
                found=True
            result = is_parent3(node,parent,tree[k],found)
            if(result):
                return True
    
    return False

def is_parent(node,parent_label,tree):
    keys = tree.keys()

    for k in keys:
        if(parent_label==k):
            result = go_to_node(node,tree[k])
            if(result!=None):
                return True
        else:
            found = is_parent(node,parent_label,tree[k])
            if(found):
                return found
    
    return False

def is_parent2(node,parent,tree):
    parent_node = go_to_node(parent,tree)
    child_node = go_to_node(node,parent_node)
    if(child_node!=None):
        return True
    return False

def find_concrete_type(types,ontology):
    results = []
    for t in types:
        found = False
        for k in types:
            if(is_parent3(k,t,ontology)):
                found=True
                break
        if(not found):
            results.append(t)
            
    return results





def update_db():
    db_manager = mongo_manager.MongoManager(configuration.db_name)
    print("connected to mongo")
    annotations = list(db_manager.db["entity"].find({"types"{"$not":{"$size":0}}))
    for annotation in annotations:
        pprint.pprint(annotation)
        concrete_types = find_concrete_type(annotation["types"],ontology)
        query={
            "_id":annotation["_id"]
        }
        update={
            "$set":{
                "concrete_types":concrete_types
            }
        }
        db_manager.db["entity"].update(query,update)
    print("done")

update_db()