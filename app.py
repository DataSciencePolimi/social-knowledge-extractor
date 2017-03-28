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

UPLOAD_FOLDER = 'data/In_csv'
ALLOWED_EXTENSIONS = set(['svg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'top secret!'

db_manager = mongo_manager.MongoManager(configuration.db_name)
app.config['OAUTH_CREDENTIALS'] = {
    'facebook': {
        'id': '470154729788964',
        'secret': '010cc08bd4f51e34f3f3e684fbdea8a7'
    },
    'twitter': {
        'id': 'NaLubGAXma7cbd9oTJQ5CZF19',
        'secret': 'D03BwxN7mjuIArji9CGOiR5uwhi5ULh99TuzOkPqiqhwEmND3c'
    }
}

lm = LoginManager(app)
lm.login_view = 'index'


@lm.user_loader
def load_user(social_id):
    print("1",social_id)
    u = list(db_manager.find("auth_users",{"social_id": social_id}))
    print(u)
    if len(u) == 0:
        return None
    print(u[0])
    return User(u[0]["social_id"],u[0]["username"] ,u[0]["email"])


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

    #TODO: create inside orchestrator
    crawler = PipelineCrawler(100,seeds[:20],id_experiment,db_manager)
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
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = list(db_manager.find("auth_users", {"social_id":social_id}))
    if len(user) == 0:
        user = User(social_id, username, email)
        db_manager.write_mongo("auth_users", {"social_id": social_id, "username":username, "email":email})
    else:
        User(user[0]["social_id"],user[0]["username"] ,user[0]["email"])
    login_user(user, True)
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
    app.run()
