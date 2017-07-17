from flask import Flask, redirect, url_for, render_template, flash,request,make_response,jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user,current_user
from knowledge_extractor.pipeline import Pipeline
from datetime import datetime
import configuration
import itertools
from bson.objectid import ObjectId
from bson.json_util import dumps
from utils import mongo_manager
from crawler.crawler_pipeline import PipelineCrawler
from crawler.crawler_dandelion import CrawlDandelion
from werkzeug.utils import secure_filename
import os
import pandas as pd
import threading
import pprint
import io, csv
from orchestrator import Orchestrator
from oauth import OAuthSignIn
from model.User import User
from utils import initialization_application_keys
from model import tweets_chunk
from utils.dandelion_interface import EntityExtraction
from pydash import py_
import json

UPLOAD_FOLDER = 'data/In_csv'
ALLOWED_EXTENSIONS = set(['svg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'top secret!'

db_manager = mongo_manager.MongoManager(configuration.db_name)
initialization_application_keys.init_application_keys(db_manager)

lm = LoginManager(app)
lm.login_view = 'index'

@lm.user_loader
def load_user(social_id):
    u = list(db_manager.find("auth_users", {"social_id": social_id}))
    if len(u) == 0:
        return None
    return User(u[0]["_id"],u[0]["social_id"],u[0]["username"] ,u[0]["email"], u[0]["access_token"],u[0]["access_token_secret"], u[0]["profile_img"])


@app.route('/')
def contacts():
    return render_template('landing.html',title='Landing')

@app.route('/home')
def index():
    return render_template('index.html',title='Home')

@app.route('/evaluate/<experiment>')
def evaluation(experiment):
    ranks = list(db_manager.getResults(ObjectId(experiment),True))
    return render_template('evaluation.html',ranks=ranks,experiment=experiment)

@app.route('/sendEvaluation/<experiment>',methods=['GET','POST'])
def registerEvaluation(experiment):

    options = {
        "upsert":True
    }
    for k,v in request.form.items():

        query={
            "handle":k,
            "experiment":ObjectId(experiment)
        }
        update={}
        if v=="true":
            update["$inc"] = {
                "correct":1
            }
        else:
            update["$inc"] = {
                "wrong":1
            }

        db_manager.register_evaluation(query,update)

    flash('Evaluation sent','success')
    return redirect("/ske/home")
    
@app.route('/results')
def get_experiments_list():
    id = list(db_manager.find("auth_users",{"social_id":current_user.social_id}))[0]["_id"]
    experiments = list(db_manager.find("experiment",{"user_id":id}).sort("creationDate",-1))
    rankings = {}
    for experiment in experiments:
        if "creationDate" in experiment:
             experiment["creationDate"] = experiment["creationDate"].strftime("%Y-%m-%d %H:%M:%S")  

        rankings[experiment["_id"]] = {
            "status":experiment["status"],
            "title":experiment.get("title","No-Title"),
            "creationDate":experiment.get("creationDate","--")
        }
    
    return render_template('experiments.html',title="My Experiments",results=rankings)

@app.route('/more')
def get_more_candidates():
    limit=20
    page = int(request.args.get('page'))
    experiment_id = request.args.get('experiment')
    skip = page*limit
    candidates = list(db_manager.getResults(ObjectId(experiment_id),True,skip))

    return dumps({
        "page":page+1,
        "candidates":candidates
    })

@app.route('/import')
def import_scenariio():
    recipe = list(db_manager.get_recipe(request.args.get("recipe")))[0]
    title = request.args.get("title")
    recipe["title"] = title
    recipe["seeds"] = recipe["seeds"][:20]
    
    return render_template("wizard.html",title="Index",scenario=recipe)

@app.route('/test')
def test():
    experiment_id = request.args.get('experiment')
    seeds = db_manager.getSeeds({"id_experiment":ObjectId(experiment_id)})
    dandelion = CrawlDandelion(True,db_manager)
    dandelion.get_all_seed_type(seeds)
    return "ok"

@app.route('/mention_graph')
def mention_graph():
    experiment_id = request.args.get('experiment')
    experiment = dict(list(db_manager.find("experiment",{"_id":ObjectId(experiment_id)}))[0])
    
    if "creationDate" in experiment:
        experiment["creationDate"] = experiment["creationDate"].strftime("%Y-%m-%d %H:%M:%S")  
    
    if "endDate" in experiment:
        experiment["endDate"] = experiment["endDate"].strftime("%Y-%m-%d %H:%M:%S") 
    
    return render_template("mentions_graph.html",title="Experiment",results=experiment)

@app.route('/mentions_graph_data')
def get_mentions_graph():
    experiment_id = request.args.get('experiment')
    seeds = db_manager.getSeeds({"id_experiment":ObjectId(experiment_id),"starting":True})
    ranks = list(db_manager.getResults(ObjectId(experiment_id)))[:100]
    rank_handles = list(map(lambda x:  x["handle"],ranks))
    ranks_origin = list(db_manager.db["rank_candidates"].find({"id_experiment":ObjectId(experiment_id),"handle":{"$in":rank_handles}}))
    result = []
    for s in seeds:
        result.append({
            "data":{
                "name":s["handle"],
                "id":s["handle"],
                "type":"seed"
            }
        })

    for r in ranks_origin:
        result.append({
            "data":{
                "name":r["handle"],
                "id":r["handle"],
                "type":"candidate",
                "score":next(item for item in ranks if item["handle"] == r["handle"])["score"]
            }
        })
        for o in r["origin"]:
            result.append({
                "data":{
                "target":r["handle"],
                "source":o,
                "id":o+"_"+r["handle"],
                "type":"me"
                }
            })
    
    tweets = list(db_manager.db["tweets"].find({"id_experiment":ObjectId("59662c9dd57606bab977a612")}))

    cooccurences = []
    for t in tweets:
        user_mentions = t["entities"]["user_mentions"]
        if(len(user_mentions)<2):
            continue
        
        handles = list(map(lambda x: x["screen_name"],user_mentions))
        cooccurences.append(handles)

    for c in cooccurences:
        combinations = itertools.combinations(c,2)
        for comb in combinations:
            if comb[0] not in rank_handles or comb[1] not in rank_handles:
                continue
            result.append({
                "data":{
                    "id":comb[0]+"_"+comb[1],
                    "source":comb[0],
                    "target":comb[1],
                    "type":"co"
                }
            })
    return jsonify(result)

@app.route('/experiment')
def get_experiment():
    experiment_id = request.args.get('experiment')
    ranks = list(db_manager.getResults(ObjectId(experiment_id),True))
    query = {
        "starting":True,
        "id_experiment":ObjectId(experiment_id),
        "hub":False
    }
    seeds = list(db_manager.getSeeds(query))
    
    for s in seeds:
        if("annotations" not in s.keys()):
            s["annotations"] = [{
                "types":["--"]
            }]
            continue
        if(len(s["annotations"])==0):
            s["annotations"].append({
                "types":["--"]
            })
            continue
        if(len(s["annotations"][0]["types"])==0):
            s["annotations"][0]["types"].append("--")
            continue

            s["annotations"]


    query["hub"] = True
    hubs = list(db_manager.getHubs(query))
    experiment = dict(list(db_manager.find("experiment",{"_id":ObjectId(experiment_id)}))[0])
    experiment["ranks"] = ranks
    experiment["seeds"] = seeds
    experiment["hubs"] = hubs
    
    if "creationDate" in experiment:
        experiment["creationDate"] = experiment["creationDate"].strftime("%Y-%m-%d %H:%M:%S")  
    
    if "endDate" in experiment:
        experiment["endDate"] = experiment["endDate"].strftime("%Y-%m-%d %H:%M:%S")  

    evaluations = list(db_manager.get_evaluations(ObjectId(experiment_id)))
    evaluationsDict = {}

    for ev in ranks:
        evaluationsDict[ev["handle"]] = {
            "correct":0,
            "wrong":0
        }
    
    
    for ev in evaluations:
        pprint.pprint(ev)
        if ev["handle"] in evaluationsDict:
            evaluationsDict[ev["handle"]]["correct"] = ev.get("correct",0)
            evaluationsDict[ev["handle"]]["wrong"] = ev.get("wrong",0)
    
    return render_template('experiment.html',title="Experiment",results=experiment,evaluations=evaluationsDict)

@app.route("/mentions_distribution")
def mention_distribution():

    experiment_id = request.args.get('experiment')
    query = {
        "starting":True,
        "id_experiment":ObjectId(experiment_id),
        "hub":False
    }
    ontology_file = open('data/dbpedia_ontology.json')
    ontology_content = ontology_file.read()
    ontology = json.loads(ontology_content)["owl:Thing"]
    seeds = list(db_manager.getSeeds(query))
    mention_distribution = db_manager.get_mention_count_by_seeds(ObjectId(experiment_id),[s["_id"] for s in seeds],ontology)
    return jsonify(mention_distribution)

@app.route('/full_results/<experiment>')
def fullResults(experiment):
    ranks = list(db_manager.getResults(ObjectId(experiment)))
    si = io.StringIO()
    cw = csv.writer(si)
    for r in ranks:
        cw.writerow([r["handle"],r["score"]])

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=export.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@app.route('/wizard')
def wizard():
    return render_template('wizard.html',title="Index",scenario={})

@app.route('/wizard_recipe')
def recipe():
    return render_template('wizard_from_recipe.html',title="Wizard")

@app.route('/run', methods=['POST'])
def run():
    if request.form.get("email") != None:
        db_manager.update("auth_users", {"social_id":current_user.social_id}, { "$set": {"email": request.form.get("email")}})
    
    experiment = {}
    hubs = []
    original_experiment_id = request.args.get('experiment')
    if original_experiment_id!=None:
        original_experiment = dict(list(db_manager.find("experiment",{"_id":ObjectId(original_experiment_id)}))[0])
    

    experiment["user_id"] = current_user._id
    
    configuration.access_token = current_user.access_token
    configuration.access_token_secret = current_user.access_token_secret
    configuration.consumer_key = configuration.providers["twitter"]["id"]
    configuration.consumer_secret = configuration.providers["twitter"]["secret"]

    #Get seeds and expert types

    if original_experiment_id!=None:
        seeds = request.form.getlist("accepted")
        experiment["original_experiment"] = ObjectId(original_experiment_id)
    #elif "recipe" in request.form:
    #    seeds = recipe["seeds"] 
    elif request.files["input_seeds"].filename == '':
        seeds = [v for k,v in request.form.items() if "prof" in k]
        pprint.pprint(seeds)
    else:
        seeds_file = request.files["input_seeds"]
        seeds_dataframe = pd.read_csv(seeds_file)
        seeds = seeds_dataframe.ix[:, 0].tolist()[:20]
    
    if original_experiment_id!=None:
        hubs = request.form.getlist("accepted-hubs")
        experiment["original_experiment"] = ObjectId(original_experiment_id)
    #elif "recipe" in request.form:
    #    seeds = recipe["seeds"] 
    elif request.files["input_hubs"].filename == '':
        hubs = [v for k,v in request.form.items() if "hub" in k and v!=""] 
        pprint.pprint(hubs)
    else:
        hubs_file = request.files["input_hubs"]
        hubs_dataframe = pd.read_csv(hubs_file)
        hubs = hubs_dataframe.ix[:, 0].tolist()[:20]
    
    if original_experiment_id!=None:
        experts = original_experiment["expert_types"]
    #elif "recipe" in request.form:
    #    experts = recipe["expertTypes"]
    elif request.files["input_expert"].filename == '':
        experts = [v for k,v in request.form.items() if "check-box" in k]
    else:
        expert_file = request.files["input_expert"]
        expert_dataframe = pd.read_csv(expert_file)
        experts = expert_dataframe.ix[:, 0].tolist()


    #Add DbPedia Types to seeds and checks dandelion rate limit
    new_seeds = []
   
    join_seeds = tweets_chunk.TweetsChunk([{"text":s}for s in seeds])

  

    datatxt = EntityExtraction(app_id=configuration.APP_ID , app_key=configuration.API_KEY_DANDELION )
    res = datatxt.nex(join_seeds.get_unique_string(), **{"include": ["types", "categories",
                                                                        "abstract", "alternate_labels"],
                                                                           "social.hashtag": True,
                                                                           "social.mention": True,
                                                                           "min_confidence":0})
    join_seeds.split_annotation_each_tweet(res["annotations"])
    for tweet in join_seeds.index_tweet:
        ann = tweet.get("annotations",[])
        if tweet['tweet']['text']!="dummy":
            if len(ann) != 0:
                new_seeds.append({"handle":tweet["tweet"]["text"], "types":ann[0].get("types",[])})
            else:
                new_seeds.append({"handle":tweet["tweet"]["text"], "types":[]})

    #End Add DBPedia

    if original_experiment_id!=None:
        experiment["title"] = "Rerun of "+original_experiment["title"]
    else:
        experiment["title"] = request.form["title"]

    experiment["email"] = list(db_manager.find("auth_users",{"social_id":current_user.social_id}))[0]["email"]
    experiment["access_token"] = current_user.access_token
    experiment["access_token_secret"] = current_user.access_token_secret
    experiment["consumer_key"] = configuration.providers["twitter"]["id"]
    experiment["consumer_secret"] = configuration.providers["twitter"]["secret"]
    experiment["expert_types"] = experts
    #experiment["tags"] = request.form.get("tags",[])
    experiment["status"] = "PROCESSING"
    experiment["creationDate"] = datetime.now()

    id_experiment = db_manager.write_mongo("experiment", dict(experiment))

    if(int(datatxt.units_left) < configuration.MIN_REQUEST_DANDELION_NEEDED):
        print("error")
        error = "No units left in our Dandelion Keys! Please Insert yours key"
        flash(error, 'error')
        return render_template('index.html',title='Error')
    else:
        # #TODO: create inside orchestrator

        db_manager.store_seeds(py_.map(new_seeds,"handle"),id_experiment)
        db_manager.store_hubs(hubs,id_experiment)

        isHub = True if len(hubs)>0 else False

        crawler = PipelineCrawler(100,id_experiment,db_manager,isHub)
        knowldege_extractor = Pipeline(db_manager,id_experiment)

        #orchestrator = Orchestrator(crawler,knowldege_extractor,id_experiment)

        threading.Thread(target=Orchestrator,
            args=(crawler,knowldege_extractor,id_experiment,db_manager),
        ).start()

        return render_template('redirect.html',title='Completed Request')

@app.route('/logout')
def logout():
    logout_user()
    return redirect("/ske/home")


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
    old_user = list(db_manager.find("auth_users", {"social_id":social_id}))
    if len(old_user) == 0:
        db_manager.write_mongo("auth_users", {"social_id": social_id, "username":username, "email":email, "access_token": access_token, "access_token_secret":access_token_secret, "profile_img":profile_img })
    else:
        db_manager.update_user_twitter(old_user[0]["_id"],access_token,access_token_secret,profile_img)
    
    db_user = list(db_manager.find("auth_users", {"social_id":social_id}))
    user = User(db_user[0]["_id"],db_user[0]["social_id"],db_user[0]["username"] ,db_user[0]["email"],db_user[0]["access_token"],db_user[0]["access_token_secret"], db_user[0]["profile_img"])

    login_user(user, remember=True)
    return redirect("/ske/home")

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
