from flask import Flask, redirect, url_for, render_template, flash,request
from flask_login import LoginManager, UserMixin, login_user, logout_user,current_user
from knowledge_extractor.pipeline import Pipeline
import configuration
from utils import mongo_manager
from crawler.crawler_pipeline import PipelineCrawler
from werkzeug.utils import secure_filename
import os
import pandas as pd
import threading
import pprint
from orchestrator import Orchestrator
from oauth import OAuthSignIn
from model.User import User
from utils import initialization_application_keys

UPLOAD_FOLDER = 'data/In_csv'
ALLOWED_EXTENSIONS = set(['svg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'top secret!'

db_manager = mongo_manager.MongoManager(configuration.db_name)
initialization_application_keys.init_application_keys()

lm = LoginManager(app)
lm.login_view = 'index'

@lm.user_loader
def load_user(social_id):
    u = list(db_manager.find("auth_users", {"social_id": social_id}))
    if len(u) == 0:
        return None
    return User(u[0]["social_id"],u[0]["username"] ,u[0]["email"], u[0]["access_token"],u[0]["access_token_secret"], u[0]["profile_img"])


@app.route('/')
def index():
    return render_template('index.html',title='Home')

@app.route('/run', methods=['POST'])
def run():
    if request.form.get("email") != None:
        db_manager.update("auth_users", {"social_id":current_user.social_id}, { "$set": {"email": request.form.get("email")}})

    pprint.pprint(request.form)

    configuration.access_token = current_user.access_token
    configuration.access_token_secret = current_user.access_token_secret
    configuration.consumer_key = configuration.providers["twitter"]["id"]
    configuration.consumer_secret = configuration.providers["twitter"]["secret"]

    dandelion_app_id = request.form["dandelion_app_id"]
    dandelion_app_key = request.form["dandelion_app_key"]

    configuration.APP1_ID = dandelion_app_id
    configuration.API_KEY_DANDELION1 = dandelion_app_key

    configuration.NUMBER_REQUEST_DANDELION = 1000

    #Get seeds and expert types
    if request.files["input_seeds"].filename == '':
        seeds = [v for k,v in request.form.items() if "prof" in k]
    else:
        seeds_file = request.files["input_seeds"]
        seeds_dataframe = pd.read_csv(seeds_file)
        seeds = seeds_dataframe.ix[:, 1].tolist()

    if request.files["input_expert"].filename == '':
        experts = [v for k,v in request.form.items() if "check-box" in k]
    else:
        expert_file = request.files["input_expert"]
        expert_dataframe = pd.read_csv(expert_file)
        experts = expert_dataframe.ix[:, 0].tolist()

    experiment = {}
    experiment["email"] = list(db_manager.find("auth_users",{"social_id":current_user.social_id}))[0]["email"]
    experiment["dandelion_app_id"] = dandelion_app_id
    experiment["dandelion_app_key"] = dandelion_app_key
    experiment["access_token"] = current_user.access_token
    experiment["access_token_secret"] = current_user.access_token_secret
    experiment["consumer_key"] = configuration.providers["twitter"]["id"]
    experiment["consumer_secret"] = configuration.providers["twitter"]["secret"]
    experiment["expert_types"] = experts
    experiment["status"] = "processing"

    id_experiment = db_manager.write_mongo("experiment", experiment)

    # #TODO: create inside orchestrator
    crawler = PipelineCrawler(100,seeds,id_experiment,db_manager)
    knowldege_extractor = Pipeline(db_manager,id_experiment)

    #orchestrator = Orchestrator(crawler,knowldege_extractor,id_experiment)

    threading.Thread(target=Orchestrator,
        args=(crawler,knowldege_extractor,id_experiment,db_manager),
    ).start()

    return render_template('redirect.html',title='Completed Request')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email, access_token, access_token_secret, profile_img  = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = list(db_manager.find("auth_users", {"social_id":social_id}))
    if len(user) == 0:
        user = User(social_id, username, email, access_token, access_token_secret, profile_img)
        db_manager.write_mongo("auth_users", {"social_id": social_id, "username":username, "email":email, "access_token": access_token, "access_token_secret":access_token_secret, "profile_img":profile_img })
    else:
        user = User(user[0]["social_id"],user[0]["username"] ,user[0]["email"],user[0]["access_token"],user[0]["access_token_secret"], user[0]["profile_img"])

    login_user(user, remember=True)
    return redirect(url_for('index'))

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
    app.run(debug=True)
