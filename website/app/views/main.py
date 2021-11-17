from flask import (
    Blueprint, flash, render_template, make_response, session,
    request, jsonify, current_app as app, url_for, abort, redirect
)

import locale
import time
import json
import requests
from searchtweets import ResultStream, gen_rule_payload, load_credentials, collect_results

main_module = Blueprint('main', __name__, template_folder='../templates')

locale.setlocale(locale.LC_ALL, '')
@main_module.route('/', methods=['GET'])
def index():
    """ Página principal
    """
    all_contracts = app.mongo.get_all_contracts()
    category_list = [(i, len(app.mongo.get_contracts_by_category(i))) for i in
                     app.mongo.get_contracts_categories()]
    category_list.sort(key=lambda x: x[1], reverse=True)
    total_money = sum(map(lambda j: j['presupuesto'] if 'presupuesto' in j.keys() else 0, all_contracts)), 2
    
    premium_search_args = tw_auth("app/config/twitter_keys.yaml")
    tweets = tw_query("comunidad madrid contrato", 10, premium_search_args)

    return render_template('index.html', numero_contratos=len(all_contracts),
                           categorias=list(category_list), dinero_total=locale.format_string("%.2f",total_money,grouping=True), tweets=tweets)

@main_module.route('/results', methods=['POST'])
def results():
    """ Aquí se llega desde el index al realizar una búsqueda.
        Se muestra el listado de contrataciones

        REFERENCIA DE QUÉ NECESITO EN EL FRONT: https://github.com/Patataman/DMyE1/issues/10
    """
    busqueda = request.form['busqueda']
    t0 = time.time()
    search = app.mongo.get_contracts_by_title(busqueda)
    tiempo = time.time() - t0
    return render_template('results.html', busqueda=busqueda, contratos=search, tiempo=tiempo)

@main_module.route('/query', methods=['GET'])
def query():
    AUTHENTICATION = requests.auth.HTTPBasicAuth(app.config['LIBREBOR_API_USER'], app.config['LIBREBOR_API_PASS'])
    sett = set()
    data = list()
    nif = request.args.get('nif')
    sett, data, n = find_data(True, nif, sett, data, ITERATE, AUTHENTICATION)
    if not VERBOSE:
        res = list()
        for item in data:
            if item["panama_papers"] or (item["type"] == "person" and item["electoral_lists"] is not None):
                res += [item]
        return jsonify(res)
    else:
        return jsonify(data)

#LIBREBOR HANDLERS

#SANDBOX: Si True utiliza la sandbox de LIBREBOR para no consumir consultas (usar con ITERATE = False)
#ITERATE: Si True utiliza el método recursivo para obtener también empresas constituidas por la original
#VERBOSE: Si True devuelve también los elementos que no aparecen en la BBDD (Para listar todos los miembros de una empresa usar con ITERATE = False)

SANDBOX = True
ITERATE = False
VERBOSE = False

if SANDBOX:
    SANDBOX = "sandbox-"
else:
    SANDBOX = ""

if ITERATE:
    ITERATE = 0
else:
    ITERATE = 20

def person_by_slug(slug, AUTHENTICATION):
    url = "https://" + SANDBOX + "api.librebor.me/v2/person/by-slug/{}/".format(slug)
    req = requests.get(url, auth=AUTHENTICATION)
    req.raise_for_status()
    req = req.json()
    return req["person"]

def company_by_nif(nif, AUTHENTICATION):
    url = "https://" + SANDBOX + "api.librebor.me/v2/company/by-nif/{}/".format(nif)
    req = requests.get(url, auth=AUTHENTICATION)
    req.raise_for_status()
    req = req.json()
    return req["company"]

def company_by_slug(slug, AUTHENTICATION):
    url = "https://" + SANDBOX + "api.librebor.me/v2/company/by-slug/{}/".format(slug)
    req = requests.get(url, auth=AUTHENTICATION)
    req.raise_for_status()
    req = req.json()
    return req["company"]

def format_person_slug(name):
    list = name.split('-')
    if len(list) >= 3:
        return ' '.join(list[2:10] + list[0:2])
    else:
        return ' '.join(list[1:10] + list[0:1])

def find_data(nif, slug, sett, data, n, AUTHENTICATION):
    if nif:
        company = company_by_nif(slug, AUTHENTICATION)
    else:
        company = company_by_slug(slug, AUTHENTICATION)
    sett.add(company["slug"])
    n += 1
    nif = False
    offshore = False #find_company_offshore(company["name"])
    dict = {
        "type":"company",
        "name":company["name"],
        "slug":company["slug"],
        "panama_papers":offshore
    }
    if "province" in company:
        dict.update({"province":company["province"]})
    if "nif" in company:
        dict.update({"nif":company["nif"]})
    if "previous_name" in company:
        dict.update({"other_names":company["previous_name"]})
    data.append(dict)
    positions = company["active_positions"] + company["inactive_positions"]
    for position in positions:
        if position["type"] == "Company" and not sett.issuperset({position["slug_company"]}) and n < 20:
            sett, data, n = find_data(nif, position["slug_company"], sett, data, n, AUTHENTICATION)
        elif position["type"] == "Person" and not sett.issuperset({position["slug_person"]}):
            sett.add(position["slug_person"])
            #offshore = find_person_offshore(position["name_person"])
            electoral = app.mongo.get_party_by_name(format_person_slug(position["slug_person"]))
            if electoral != list([]):
                electoral = electoral[0]["partido"]
            else:
                electoral = None
            data.append({
                "type":"person",
                "name":position["name_person"],
                "slug":position["slug_person"],
                "role":position["role"],
                "company":company["name"],
                "panama_papers":offshore,
                "electoral_lists":electoral
            })
    return sett, data, n

#def find_company_offshore(company)

#def find_person_offshore(person)

def tw_auth(twitter_keys_yaml_path):
  premium_search_args = load_credentials(twitter_keys_yaml_path, yaml_key="search_tweets_premium", env_overwrite=False)
  return premium_search_args

def tw_query(str_query, n_results, premium_search_args, from_date = "2021-09-01"):
  rule = gen_rule_payload(str_query, from_date=from_date, results_per_call=n_results)
  rs = ResultStream(rule_payload=rule,
                  max_results=500,
                  max_pages=1,
                  **premium_search_args)
  return list(rs.stream())
