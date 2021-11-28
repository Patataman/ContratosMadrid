from pymongo import MongoClient
from collections import defaultdict
from tqdm import tqdm

import json
import requests

mongo = MongoClient()["dme"]


def format_person_slug(name):
    lname = name.split('-')
    if len(lname) >= 3:
        return ' '.join(lname[2:10] + lname[0:2])
    else:
        return ' '.join(lname[1:10] + lname[0:1])


def update_contracts_with_nif(nif, data):
    return mongo["contracts"].update_many(
        {"adjudicacion.nif adjudicatario": nif},
        {"$set": data}
    )


# recupera los que tienen adjudicaciones
adjudicados = mongo["contracts"].find({"adjudicacion": { "$exists" : True }})

nifs = defaultdict(int)
for contrato in adjudicados:
    nifs[contrato['adjudicacion']['nif adjudicatario']] += 1

nifs_ordenados = dict(sorted(nifs.items(), key=lambda item: item[1], reverse=True))

keys = [k for k in nifs_ordenados.keys()]

for nif in tqdm(keys):
    contract = mongo["contracts"].find_one({"adjudicacion.nif adjudicatario": nif})
    if "librebor" not in contract:
        continue

    for bor in contract['librebor']:
        if bor['type'] == "person":
            name = bor['name'].split(" ")
            query = [{"$unwind": "$names"}]
            for n in name:
                query.append({
                    "$match": {
                        'names': {'$regex': f".*{n}.*", '$options': 'i'}
                    }
                })
            match_offshore = [k for k in mongo['offshore'].aggregate(query)]
            if len(match_offshore) > 0 and \
               any([len(bor['name']) == m['names'] for m in match_offshore]):
                bor['panama_papers'] = True

        if bor['type'] == "company":
            name = bor['slug'].split("-")
            query = [{"$unwind": "$names"}]
            for n in name:
                query.append({
                    "$match": {
                        'names': {'$regex': f".*{n}.*", '$options': 'i'}
                    }
                })
            match_offshore = [k for k in mongo['offshore'].aggregate(query)]
            if len(match_offshore) > 0:
                for m in match_offshore[:]:
                    m['names'] = m['names'].lower().split(" ")
                    for palabra in name:
                        palabra = palabra.lower()
                        if palabra in m['names']:
                            # Para nombres como Johnson & Johnson que no haga match con
                            # Johnson manolete
                            m['names'].pop(m['names'].index(palabra))
                for m in match_offshore:
                    if len(m['names']) == 0:
                        bor['panama_papers'] = True
                    elif len(m['names']) == 1 and "sl" in m['names']:
                        bor['panama_papers'] = True
