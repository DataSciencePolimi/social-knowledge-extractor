__author__ = 'marcotagliabue'

import configuration
from utils import mongo_manager

def init_application_keys(db_manager):

    dandelion = list(db_manager.get_dandelion_keys())
    configuration.API_KEY_DANDELION = dandelion[0]["key_dandelion"]
    configuration.APP_ID = dandelion[0]["app_id"]
    

    twitter = list(db_manager.get_twitter_keys())
    configuration.providers["twitter"]["id"] = twitter[0]["consumer_key"]
    configuration.providers["twitter"]["secret"] = twitter[0]["consumer_secret"]

