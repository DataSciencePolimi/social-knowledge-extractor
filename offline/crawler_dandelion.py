__author__ = 'marcotagliabue'
import math
import logging
import pprint
import json
from dandelion import DataTXT

from dandelion.base import DandelionException

import configuration
from utils import mongo_manager
from model import tweets_chunk


class CrawlDandelion:
    def __init__(self, one_dandelion_key,db_manager):
        self.db_manager = db_manager
        self.one_dandelion_key = one_dandelion_key
        ontology_file = open('crawler/dbpedia_ontology.json')
        ontology_content = ontology_file.read()
        ontology = json.loads(ontology_content)["owl:Thing"]
        self.ontology = ontology
    
    def start(self,id_experiment):
       