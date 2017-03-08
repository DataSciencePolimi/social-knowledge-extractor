from flask import Flask

from utils.DBManager import DBManager
from knowledge_extractor.pipeline import Pipeline

app = Flask(__name__)

@app.route('/start')
def start_pipeline():
    dbManager = DBManager("ske_db")    
    
    pipeline = Pipeline(dbManager,"./knowledge_extractor/data/expert_types.csv")
    pipeline.run()
    return 'Hello, World!'

if __name__=="main":
    app.run()