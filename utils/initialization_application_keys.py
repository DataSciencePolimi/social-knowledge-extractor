__author__ = 'marcotagliabue'

import configuration
from utils import mongo_manager

def init_application_keys(db_manager):

    dandelion = list(db_manager.get_dandelion_keys())
    configuration.API_KEY_DANDELION = dandelion[0]["key_dandelion"]
    configuration.APP_ID = dandelion[0]["app_id"]
    configuration.API_KEY_DANDELION2 = dandelion[1]["key_dandelion"]
    configuration.APP2_ID = dandelion[1]["app_id"]
    configuration.API_KEY_DANDELION3 = dandelion[2]["key_dandelion"]
    configuration.APP3_ID = dandelion[2]["app_id"]
    configuration.API_KEY_DANDELION4 = dandelion[3]["key_dandelion"]
    configuration.APP4_ID = dandelion[3]["app_id"]

    twitter = list(db_manager.find("application_keys", {"service":"twitter"}))
    configuration.providers["twitter"]["id"] = twitter[0]["consumer_key"]
    configuration.providers["twitter"]["secret"] = twitter[0]["consumer_secret"]

