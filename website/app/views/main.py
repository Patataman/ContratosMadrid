from app.views.utils import librebor_find_data, tw_auth, tw_query
from collections import defaultdict
from flask import (
    Blueprint, flash, render_template, make_response, session,
    request, jsonify, current_app as app, url_for, abort, redirect
)

import json
import locale
import requests
import time


TW_AUTH = tw_auth("app/config/twitter_keys.yaml")

main_module = Blueprint('main', __name__, template_folder='../templates')


locale.setlocale(locale.LC_ALL, '')
@main_module.route('/', methods=['GET'])
def index():
    """ Página principal
    """
    ## Cosas de contratos
    all_contracts = app.mongo.get_all_contracts().count()
    category_list = [(i, app.mongo.get_contracts_by_category(i).count()) for i in
                     app.mongo.get_contracts_categories()]
    category_list.sort(key=lambda x: x[1], reverse=True)

    total_money = str(app.mongo.get_total_money())
    if len(total_money.split(".")[0]) > 7:
        # Para escribir en Millones
        total_money = total_money.split(".")[0]
        total_money = total_money[:-6]
        total_money = locale.format_string("%.0f", float(total_money), grouping=True) + " M"
    else:
        total_money = locale.format_string("%.2f", total_money, grouping=True)
    #########################

    ######### Localizaciones para el mapa
    # empresas únicas en la bbdd
    companies = app.mongo.unique_company()

    # Recuperamos los contratos por empresa
    top_nifs = app.mongo.get_aggregate_contracts([
        {"$match": {"adjudicacion": { "$exists" : True }}},
        {"$group": {
            "_id": "$adjudicacion.nif adjudicatario",
            "count": { "$sum": 1 }}
        }
    ])
    # Convierte esto en un diccionario para agilizar búsqueda
    top_nifs = {d['_id']: d['count'] for d in top_nifs}

    contratos_por_localidad = defaultdict(int)
    for doc in companies:
        localidad = doc['document']['province']
        contratos_por_localidad[localidad] += top_nifs[doc['_id']]

    locations = defaultdict(dict)
    for province, count in contratos_por_localidad.items():
        resp = requests.get(
            f"https://maps.googleapis.com/maps/api/geocode/json?address={province}&region=es&key={app.config['GOOGLE_API']}"
        )
        if resp.status_code == 200:
            nombre = resp.json()['results'][0]['address_components'][0]['short_name']
            if nombre not in locations:
                locations[nombre]['center'] = resp.json()['results'][0]['geometry']['location']
                locations[nombre]['count'] = count
            else:
                locations[nombre]['count'] += count
    ##################

    # Feed de Twitter
    tweets = tw_query("comunidad madrid contrato", 10, TW_AUTH)
    ######

    return render_template(
        'index.html', numero_contratos=all_contracts, categorias=list(category_list),
        dinero_total=total_money, companies_locations=locations, tweets=tweets
    )


@main_module.route('/results', methods=['POST'])
def results():
    """ Aquí se llega desde el index al realizar una búsqueda.
        Se muestra el listado de contrataciones

        REFERENCIA DE QUÉ NECESITO EN EL FRONT: https://github.com/Patataman/DMyE1/issues/10
    """
    busqueda = request.form['busqueda']
    t0 = time.time()
    search = list(app.mongo.get_contracts_by_title(busqueda).limit(50))
    tiempo = time.time() - t0
    return render_template('results.html', busqueda=busqueda, contratos=search, tiempo=tiempo)


@main_module.route('/query', methods=['GET'])
def query():
    """ API NIF = B49154818
        Sandbox NIF = A46103834

        Función para hacer la búsqueda en LibreBor de la empresa solicitada.
        Argumentos GET: nif y company
        A esto solo se le debería llamar si el contrato recuperado no tiene
        la clave "librebor"
    """
    # VERBOSE: Si True devuelve también los elementos que no aparecen en la BBDD
    VERBOSE = False

    auth = requests.auth.HTTPBasicAuth(app.config['LIBREBOR_API_USER'], app.config['LIBREBOR_API_PASS'])
    slug = request.args.get('nif')
    contract_id = request.args.get('contract')

    visited, results, iterations = librebor_find_data(app.mongo, True, slug, auth)

    if not VERBOSE:
        res = list()
        for item in results:
            if item["panama_papers"] or (item["type"] == "person" and item["electoral_lists"] is not None):
                res += [item]

        # Si hay resultados actualizamos los datos del contrato
        # Por un lado actualizamos el contrato
        app.mongo.update_contract(request.args.get('contract'), {"librebor": res})
        # Por otro añadimos la empresa a nuestra bbdd
        for r in results:
            if r['type'] == "company":
                app.mongo.add_company(r)

        return jsonify(res)
    else:
        return jsonify(results)
