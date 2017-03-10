import pprint
import pandas as pd
import collections

from .strategies.AST import AST
from .strategies.EHE import EHE


class Pipeline:

    def parseExpertFile(self):
        experts = []
        with open('../data/expert_types.csv') as f:
            experts = f.readlines() 
        
        experts = [x.strip() for x in experts]
          
        return experts

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
            vector[k] = {}
            for s in space:
                vector[k][s] = c[s]
        
        return pd.DataFrame(vector)
        

    def getSeeds(self):
        query = {}
        return self.db.getSeeds(query)

    def getCandidates(self):
        query = {}
        return self.db.getCandidates(query)
    
    def computeVectors(self,seeds):
        mentions = {}
        ast_mentions = {}
        
        print("Running the strategies")
        ehe = EHE(self.db,self.expertFile)
        ast = AST(self.db,self.expertFile)
        
        for seed in seeds:
            #computer array of mentioned entity
            mentions[seed["_id"]] = ehe.getEntities(seed)
            ast_mentions[seed["_id"]] = ast.getEntities(seed)
        
        space_ehe = self.createSpace(mentions)
        space_ast = self.createSpace(ast_mentions)

        print("Creating feature vector")
        
        seed_feature_vectors_ast = self.createFeatureVector(space_ast,ast_mentions) 
        seed_feature_vectors_ehe = self.createFeatureVector(space_ehe,mentions)

        seed_feature_vectors = seed_feature_vectors_ast.append(seed_feature_vectors_ehe)
        return seed_feature_vectors

    def run(self):

        feature_vectors = {}

        seeds = self.getSeeds()
        candidates = self.getCandidates()

        print("Computing seeds fv")
        feature_vectors["seeds"] = self.computeVectors(seeds)
        print("Computing candidates fv")
        feature_vectors["candidates"] = self.computeVectors(candidates)

        return feature_vectors

    def __init__(self,db,expertFile):
        self.db=db
        self.expertFile = [
                "http://dbpedia.org/ontology/Broadcaster",
                "http://dbpedia.org/ontology/Artist",
                "http://dbpedia.org/ontology/Magazine",
                "http://dbpedia.org/ontology/model",
                "http://dbpedia.org/ontology/Organisation",
                "http://dbpedia.org/ontology/TelevisionShow"
                ]
