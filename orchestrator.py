from utils import mongo_manager

class Orchestrator(object):
    
    def run(self):
        print("Orchestrator: starting crawling pipeline")
        user = list(self.db_manager.find("experiment",{"_id":self.id_experiment}))[0]
        user["status"] = "CRAWLING"
        self.db_manager.update("experiment",{"_id":self.id_experiment}, user)

        self.crawler.run()

        user = list(self.db_manager.find("experiment",{"_id":self.id_experiment}))[0]
        user["status"] = "COMPUTING_CANDIDATES"
        self.db_manager.update("experiment",{"_id":self.id_experiment}, user)
        
        print("Orchestrator: starting knowledge extractor pipeline")
        self.knowledge_extractor.run()

        user = list(self.db_manager.find("experiment",{"_id":self.id_experiment}))[0]
        user["status"] = "COMPLETED"
        self.db_manager.update("experiment",{"_id":self.id_experiment}, user)

    def __init__(self,crawler,knowldege_extractor,id_experiment):
        self.crawler=crawler
        self.knowledge_extractor=knowldege_extractor
        self.id_experiment = id_experiment
        