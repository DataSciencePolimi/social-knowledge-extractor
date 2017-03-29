__author__ = 'marcotagliabue'

import json
import pprint

new_dict = {}
def myprint(d):
    for k, v in d.items():
        new_dict["text"] = k

        if v != {}:
           new_dict["nodes"] = [myprint(v)]
        else:
            return {"text":k}

with open("../data/dbpedia_ontology.json") as data_file:
    data = json.load(data_file)

def compact_to_verbose(compact):
    dummy = []
    for key, value in compact.items():
        d = {}
        if value != {}:
            d['text'] = key
            d['nodes'] = compact_to_verbose(value)
        else:
            d['text'] = key

        d["icon"] = "glyphicon@@@@glyphicon-stop"
        d["selectedIcon"] = "glyphicon@@@@glyphicon-stop"
        d["color"] =  "#000000"
        d["backColor"] = "#FFFFFF"
        d["selectable"] = True
        d["state"] = {
            "checked": True,
            "disabled": True,
            "expanded": True,
            "selected": True
        }

        dummy.append(d)

    return dummy

pprint.pprint(compact_to_verbose(data))
