from utils import mongo_manager
from datetime import datetime

class Orchestrator(object):
    
    def run(self):
        print("Orchestrator: starting crawling pipeline")
        experiment = list(self.db_manager.find("experiment",{"_id":self.id_experiment}))[0]
        experiment["status"] = "CRAWLING"
        experiment["crawlingDate"] = datetime.now()
        self.db_manager.update("experiment",{"_id":self.id_experiment}, experiment)

        self.crawler.run()

        experiment = list(self.db_manager.find("experiment",{"_id":self.id_experiment}))[0]
        experiment["status"] = "COMPUTING_CANDIDATES"
        experiment["computationDate"] = datetime.now()
        self.db_manager.update("experiment",{"_id":self.id_experiment}, experiment)
        
        print("Orchestrator: starting knowledge extractor pipeline")
        self.knowledge_extractor.run()

        experiment = list(self.db_manager.find("experiment",{"_id":self.id_experiment}))[0]
        experiment["status"] = "COMPLETED"
        experiment["endDate"] = datetime.now()
        self.db_manager.update("experiment",{"_id":self.id_experiment}, experiment)

    def __init__(self,crawler,knowldege_extractor,id_experiment,db_manager):
        self.crawler=crawler
        self.knowledge_extractor=knowldege_extractor
        self.id_experiment = id_experiment
        self.db_manager= db_manager 
        self.run()

