__author__ = 'marcotagliabue'
from flask import Flask
from flask_restful import Resource, Api
from flask_restful import reqparse
from Services import mongo_manager
import configuration
from bson.json_util import dumps
from bson.objectid import ObjectId
from pipeline import Pipeline

app = Flask(__name__)
api = Api(app)
configuration.db_name = configuration.db_name_web
db_manager = mongo_manager.MongoManager(configuration.db_name)

class AppKeys(Resource):
    def post(self):
        # Parse the arguments
        parser = reqparse.RequestParser()
        parser.add_argument('twitter_access_token', type=str, help='Access Token from Twitter')
        parser.add_argument('twitter_access_token_secret', type=str, help='Secret token from Twitter')
        parser.add_argument('twitter_consumer_key', type=str, help='Consumer Key from Twitter')
        parser.add_argument('twitter_consumer_secret', type=str, help='Consumer Secret from Twitter')
        parser.add_argument('dandelion_id', type=str, help='App ID from Dandelion')
        parser.add_argument('danndelion_key', type=str, help='App Key from Dandelion')

        args = parser.parse_args()
        _id = str(db_manager.write_mongo("user", args))
        print(_id)

        return {"_id":_id}

api.add_resource(AppKeys, '/app_keys')

class Seed(Resource):
    def post(self):
        # Parse the arguments
        parser = reqparse.RequestParser()
        parser.add_argument('seeds', action='append', help='Starting_Seeds')
        parser.add_argument('expert_types', action='append', help='Types selected by Expert')
        parser.add_argument('user_id', type=str, help='User Token')
        args = parser.parse_args()

        db_manager.write_mongo("user_seeds", args)

        print(args)

class Run(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=str, help='User Token')
        args = parser.parse_args()
        user_data = list(db_manager.find("user",{"_id":ObjectId(args["user_id"])}))[0]
        print(user_data)

        configuration.access_token = user_data["twitter_access_token"]
        configuration.access_token_secret = user_data["twitter_access_token_secret"]
        configuration.consumer_key = user_data["twitter_consumer_key"]
        configuration.consumer_secret = user_data["twitter_consumer_key"]
        configuration.API_KEY_DANDELION = user_data["danndelion_key"]
        configuration.APP_ID = user_data["dandelion_id"]

        seeds = list(db_manager.find("user_seeds",{"user_id":args["user_id"]}))[0]["seeds"]
        print(seeds)
        Pipeline(100, seeds) #Starting time 15:24

        return {"message":"Pipeline started! Come back later with your token"}

api.add_resource(Run, '/run')


api.add_resource(Seed, '/seeds')

if __name__ == '__main__':
    app.run(threaded=True, debug=True,host='0.0.0.0')