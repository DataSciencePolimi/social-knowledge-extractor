from flask import Flask, render_template, request,session
from knowledge_extractor.pipeline import Pipeline
import configuration
from utils import mongo_manager
from crawler.crawler_pipeline import PipelineCrawler
from werkzeug.utils import secure_filename
import os
import pandas as pd
import threading
import pprint
import orchestrator

UPLOAD_FOLDER = 'data/In_csv'
ALLOWED_EXTENSIONS = set(['svg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db_manager = mongo_manager.MongoManager(configuration.db_name)

@app.route('/')
def index():
    return render_template('index.html',title='Home')

@app.route('/run', methods=['POST'])
def run():

    configuration.access_token = request.form["access_token"]
    configuration.access_token_secret = request.form["access_token_secret"]
    configuration.consumer_key = request.form["consumer_key"]
    configuration.consumer_secret = request.form["consumer_secret"]

    dandelion_app_id = request.form["dandelion_app_id"]
    dandelion_app_key = request.form["dandelion_app_key"]

    print(dandelion_app_id, dandelion_app_key)

    configuration.APP1_ID = dandelion_app_id
    configuration.API_KEY_DANDELION1 = dandelion_app_key

    configuration.NUMBER_REQUEST_DANDELION = 1000

    diction = {k:v[0] for (k,v) in dict(request.form).items()}
    diction["status"] = "processing"

    seeds_file = request.files["input_seeds"]
    seeds_dataframe = pd.read_csv(seeds_file)
    seeds = seeds_dataframe.ix[:, 1].tolist()

    expert_file = request.files["input_expert"]
    expert_dataframe = pd.read_csv(expert_file)
    experts = expert_dataframe.ix[:, 0].tolist()
    diction["expert_types"] = experts

    id_experiment = db_manager.write_mongo("experiment", diction)

    crawler = PipelineCrawler(100,seeds[:20],id_experiment,db_manager)
    knowldege_extractor = Pipeline(db_manager)

    orchestrator = Orchestrator(crawler,knowldege_extractor,id_experiment)

    threading.Thread(target=orchestrator,
        args=(db_manager,id_experiment),
    ).start()

    return render_template('redirect.html',title='Completed Request')


@app.route('/start')
def start_pipeline():
    #dbManager = DBManager("ske_db",1)
    
    #pipeline = Pipeline(dbManager)
    #scores  = pipeline.run()
    #_thread.start_new_thread(Pipeline, (db_manager,1))

  

    #pprint.pprint(fv["seeds"].head())
    #fv["candidates"].to_csv("cand_fv.csv")
    #fv["seeds"].to_csv("seed_fv.csv")
    return render_template('redirect.html',title='Completed Request')

if __name__ == '__main__':
    app.run()
