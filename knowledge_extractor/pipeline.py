import pprint

from .strategies.AST import AST
from .strategies.EHE import EHE


class Pipeline:

    def parseExpertFile(self):
        experts = []
        with open('../data/expert_types.csv') as f:
            experts = f.readlines() 
        
        experts = [x.strip() for x in experts]
          
        return experts


    def getSeeds(self):
        query = {}
        return self.db.getSeeds(query)

    def getCandidates(self):
        query = {}
        return self.db.getCandidates(query)

    def run(self):

        seeds = self.getSeeds()
        ehe = EHE(self.db,self.expertFile)
        ast = AST(self.db,self.expertFile)
        
        mentions = {}
        ast_mentions = {}
        for seed in seeds:
            #computer array of mentioned entity
            mentions[seed["_id"]] = ehe.getEntities(seed)
            ast_mentions[seed["_id"]] = ast.getEntities(seed)
        
        pprint.pprint(ast_mentions)

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
