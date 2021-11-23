from pymongo import MongoClient
from collections import defaultdict
from tqdm import tqdm

import json
import requests
import re

mongo = MongoClient()["dme"]
contratos = mongo["contracts"]


def query_format(str):
    return re.sub(
        '[aAáÁ]', '[aAáÁ]',
        re.sub('[eEéÉ]', '[eEéÉ]',
               re.sub('[iIíÍ]', '[iIíÍ]',
                      re.sub('[oOóÓ]', '[oOóÓ]',
                             re.sub('[uUúüÚÜ]', '[uUúüÚÜ]',
                                    re.sub('[nNñÑ]', '[nNñÑ]',
                                           re.sub(' +', '.*', str)
                                          )
                                   )
                            )
                     )
              )
    )


def format_person_slug(name):
    lname = name.split('-')
    if len(lname) >= 3:
        return ' '.join(lname[2:10] + lname[0:2])
    else:
        return ' '.join(lname[1:10] + lname[0:1])


def get_party_by_name(name):
    return list(mongo["electoral_list"].find(
        {'candidatos': {
            '$regex': f".*{query_format(name)}.*", '$options': 'xsi'
        }},
        {'partido': 1, '_id': 0}
    ))


def update_contracts_with_nif(nif, data):
    return mongo["contracts"].update_many(
        {"adjudicacion.nif adjudicatario": nif},
        {"$set": data}
    )


def company_by_nif(nif, auth):
    url = f"https://api.librebor.me/v2/company/by-nif/{nif}/"
    req = requests.get(url, auth=auth)
    try:
        req.raise_for_status()
    except Exception as e:
        return False, {}
    req = req.json()
    return True, req["company"]


def librebor_find_data(slug, auth):
    ok, company = company_by_nif(
        slug, auth
    )
    if not ok:
        return []

    offshore = False

    output = {
        "type": "company",
        "name": company["name"],
        "slug": company["slug"],
        "panama_papers": offshore
    }

    if "province" in company:
        output.update({"province": company["province"]})
    if "nif" in company:
        output.update({"nif": company["nif"]})
    if "previous_name" in company:
        output.update({"other_names": company["previous_name"]})

    results = [output]
    visited = set()
    positions = company["active_positions"] + company["inactive_positions"]
    for position in positions:
        if position["type"] == "Person" and not visited.issuperset({position["slug_person"]}):
            visited.add(position["slug_person"])

            electoral = get_party_by_name(format_person_slug(position["slug_person"]))
            if electoral != list([]):
                electoral = electoral[0]["partido"]
            else:
                electoral = None

            results.append({
                "type": "person",
                "name": position["name_person"],
                "slug": position["slug_person"],
                "role": position["role"],
                "company": company["name"],
                "panama_papers": False,
                "electoral_lists": electoral
            })

    return results


# recupera los que tienen adjudicaciones
adjudicados = contratos.find({"adjudicacion": { "$exists" : True }})
contar = contratos.count_documents({"adjudicacion": { "$exists" : True }})
print(f"Hay {contar} contratos adjudicados")
nifs = defaultdict(int)
for contrato in adjudicados:
    nifs[contrato['adjudicacion']['nif adjudicatario']] += 1

nifs_ordenados = dict(sorted(nifs.items(), key=lambda item: item[1], reverse=True))

config = json.load(open("config.json"))
auth = requests.auth.HTTPBasicAuth(
    config['LIBREBOR_API_USER'],
    config['LIBREBOR_API_PASS']
)

keys = [k for k in nifs_ordenados.keys()]

for nif in tqdm(keys[:200]):
    data = librebor_find_data(nif, auth)
    # Codigo por si no se han actualizado los que deberían
    # data = mongo['contracts'].find({"adjudicacion.nif adjudicatario": nif})[0]['librebor']

    # contratos con ese nif en adjudicacion
    update_contracts_with_nif(nif, {"librebor": data})

    for d in data:
        if d['type'] == "company":
            try:
                mongo["company"].insert_one(d)
            except pymongo.errors.DuplicateKeyError:
                pass
            except Exception as e:
                raise e
