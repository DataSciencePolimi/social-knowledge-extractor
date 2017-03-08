from utils.DBManager import DBManager
from pipeline import Pipeline

import pprint

if __name__ == "__main__":
    # Input seeds
    dbManager = DBManager("ske_db")    
    
    pipeline = Pipeline(dbManager,"./data/expert_types.csv")
    pipeline.run()