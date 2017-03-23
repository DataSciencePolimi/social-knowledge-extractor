__author__ = 'marcotagliabue'

import configuration
import pandas as pd
from utils import mongo_manager
from crawler.crawler_pipeline import PipelineCrawler
from orchestrator import Orchestrator
from knowledge_extractor.pipeline import Pipeline
import sys
from bson import ObjectId

# DANDELION API KEYS
configuration.API_KEY_DANDELION1 = sys.argv[1]
configuration.APP1_ID = sys.argv[2]
configuration.API_KEY_DANDELION2 = sys.argv[3]
configuration.APP2_ID = sys.argv[4]
configuration.API_KEY_DANDELION3 = sys.argv[5]
configuration.APP3_ID = sys.argv[6]
configuration.API_KEY_DANDELION4 = sys.argv[7]
configuration.APP4_ID = sys.argv[8]

# Twitter API
configuration.access_token = sys.argv[9]
configuration.access_token_secret = sys.argv[10]
configuration.consumer_key = sys.argv[11]
configuration.consumer_secret = sys.argv[12]

db_manager = mongo_manager.MongoManager(configuration.db_name)

def run_scenario(scenario):
    diction = {"email":"marco.tagliabue@"+scenario+".com"}
    diction["status"] = "processing"

    seeds_dataframe = pd.read_csv("../data/In_csv/"+scenario+"/seed.csv")
    seeds = seeds_dataframe.ix[:, 1].tolist()

    expert_dataframe = pd.read_csv("../data/In_csv/"+scenario+"/expert_types.csv")
    experts = expert_dataframe.ix[:, 0].tolist()
    diction["expert_types"] = experts

    id_experiment = db_manager.write_mongo("experiment", diction)

    crawler = PipelineCrawler(100,seeds,id_experiment,db_manager)
    knowldege_extractor = Pipeline(db_manager,id_experiment)

    orchestrator = Orchestrator(crawler,knowldege_extractor,id_experiment, db_manager)

    return id_experiment

def create_rank(id_experiment, scenario):
    dataframe = pd.DataFrame(list(db_manager.find("rankings",{"experiment_id":id_experiment})))
    dataframe.to_csv("../data/Out_csv/"+scenario+".csv", index=False)

if __name__ == '__main__':
    print(sys.argv)
    scenario = ["au", "expo", "fashion", "finance"]
    id_experiment = run_scenario(scenario[1])
    create_rank(id_experiment, scenario[1])


