
class Orchestrator(object):
    
    def run(self):
        print("Orchestrator: starting crawling pipeline")
        self.crawler.run()
        print("Orchestrator: starting knowledge extractor pipeline")
        self.knowledge_extractor.run()

    def __init__(self,crawler,knowldege_extractor,id_experiment):
        self.crawler=crawler
        self.knowledge_extractor=knowldege_extractor
        self.id_experiment = id_experiment
        