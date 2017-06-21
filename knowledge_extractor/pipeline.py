import pprint
import pandas as pd
import collections
from scipy.spatial.distance import cosine
from .strategies.AST import AST
from .strategies.EHE import EHE
from flask import current_app

class Pipeline:

    def createSpace(self,seeds):
        print("Creating the vector space")
        space = []
        for k,v in seeds.items():
            space += v
        
        space = set(space)
        return space
    
    def createFeatureVector(self,space,data):
        vector = {}
        for k,v in data.items():
            c = collections.Counter(v)
            for s in space:
                if s not in vector:
                    vector[s] = {}
                vector[s][k] = c[s]
        
        return pd.DataFrame(vector)
        

    def getSeeds(self):
        query = {"id_experiment":self.experiment_id, "starting":True, "hub":False}
        return self.db.getSeeds(query)

    def getCandidates(self):
        query = {"id_experiment":self.experiment_id, "starting":False, "hub":False}
        return self.db.getCandidates(query)
    
    def computeSeedVectors(self,seeds):
        mentions = {}
        ast_mentions = {}
        

        ehe = EHE(self.db,self.expertFile)
        ast = AST(self.db,self.expertFile)
        
        for seed in seeds:
            #computer array of mentioned entity
            pprint.pprint(seed)
            mentions[seed["handle"]] = ehe.getEntities(seed)
            ast_mentions[seed["handle"]] = ast.getEntities(seed)
        
        pprint.pprint(ast_mentions)
        space_ehe = self.createSpace(mentions)
        space_ast = self.createSpace(ast_mentions)

        print("Creating feature vector for the seed")
        
        seed_feature_vectors_ast = self.createFeatureVector(space_ast,ast_mentions)*(1-self.alfa) 
        seed_feature_vectors_ehe = self.createFeatureVector(space_ehe,mentions)*self.alfa

        seed_feature_vectors = seed_feature_vectors_ast.join(seed_feature_vectors_ehe)
        
        return {
            "fv":seed_feature_vectors,
            "space_ehe":space_ehe,
            "space_ast":space_ast
        }
    
    def createCentroid(self,seeds):
        return seeds.mean()
    
    def computeCandidatesVectors(self,cands,space_ast,space_ehe):
        mentions = {}
        ast_mentions = {}
        
        ehe = EHE(self.db,self.expertFile)
        ast = AST(self.db,self.expertFile)
        
        for cand in cands:
            #computer array of mentioned entity
            print("Getting mentions for candidate " + cand["handle"])
            mentions[cand["handle"]] = ehe.getEntities(cand)
            ast_mentions[cand["handle"]] = ast.getEntities(cand)
        
        print("Creating feature vector for the candidates")
        
        cands_feature_vectors_ast = self.createFeatureVector(space_ast,ast_mentions)*(1-self.alfa) 
        cands_feature_vectors_ehe = self.createFeatureVector(space_ehe,mentions)*self.alfa


        cands_feature_vectors = cands_feature_vectors_ast.join(cands_feature_vectors_ehe)
       
        return cands_feature_vectors

    def run(self):

        feature_vectors = {}

        seeds = self.getSeeds()
        candidates = self.getCandidates()

        print("Computing seeds fv")
        seeds_components = self.computeSeedVectors(seeds)
       
        feature_vectors["seeds"] = seeds_components["fv"]
        print("Computing candidates fv")
        pprint.pprint(seeds_components["fv"])
        feature_vectors["candidates"] = self.computeCandidatesVectors(candidates,seeds_components["space_ast"],seeds_components["space_ehe"])
        
        centroid = self.createCentroid(feature_vectors["seeds"])
        centroid = centroid.values

        scores = feature_vectors["candidates"].apply(lambda row: 1-cosine(row,centroid),axis=1)
        
        print("Saving the rankings")
        self.db.saveScores(scores,self.experiment_id)
        
        return scores

    def __init__(self,db,experiment_id):
        self.alfa=0.7
        self.db=db
        self.experiment_id = experiment_id
        self.expertFile = self.db.getExpertTypes(experiment_id)

if __name__ == "__main__":
     import mongo_manager
     import configuration
     from bson import ObjectId
     db_manager = mongo_manager.MongoManager(configuration.db_name)

     kn = Pipeline(db_manager, ObjectId('594142ebd576065c263fc798'))
     kn.run()
