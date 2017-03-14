from flask import Flask, render_template, request,session
from utils.DBManager import DBManager
from knowledge_extractor.pipeline import Pipeline
import configuration
from utils import mongo_manager
from crawler import crawler_pipeline
from werkzeug.utils import secure_filename
import os
import pandas as pd
import _thread
import pprint

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

    configuration.APP2_ID = dandelion_app_id
    configuration.API_KEY_DANDELION2 = dandelion_app_key
    configuration.APP3_ID = dandelion_app_id
    configuration.API_KEY_DANDELION3 = dandelion_app_key
    configuration.APP4_ID = dandelion_app_id
    configuration.API_KEY_DANDELION4 = dandelion_app_key
    configuration.NUMBER_REQUEST_DANDELION = 250

    diction = {k:v[0] for (k,v) in dict(request.form).items()}
    diction["status"] = "processing"

    id_experiment = db_manager.write_mongo("user", diction)

    seeds_file = request.files["input_seeds"]
    seeds_dataframe = pd.read_csv(seeds_file)
    seeds = seeds_dataframe.ix[:, 1].tolist()
    _thread.start_new_thread(crawler_pipeline.PipelineCrawler, (100,seeds,id_experiment))

    return render_template('redirect.html',title='Completed Request')


@app.route('/start')
def start_pipeline():
    dbManager = DBManager("ske_db")
    
    pipeline = Pipeline(dbManager,"./knowledge_extractor/data/expert_types.csv")
    scores  = pipeline.run()

    #pprint.pprint(fv["seeds"].head())
    #fv["candidates"].to_csv("cand_fv.csv")
    #fv["seeds"].to_csv("seed_fv.csv")
    return scores

if __name__ == '__main__':
    app.run()
