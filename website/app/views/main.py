from flask import (
    Blueprint, flash, render_template, make_response, session,
    request, jsonify, current_app as app, url_for, abort, redirect
)
from app.views.utils import librebor_find_data, tw_auth, tw_query

import time
import json
import requests
import locale


main_module = Blueprint('main', __name__, template_folder='../templates')

TW_AUTH = tw_auth("app/config/twitter_keys.yaml")

locale.setlocale(locale.LC_ALL, '')
@main_module.route('/', methods=['GET'])
def index():
    """ Página principal
    """
    all_contracts = app.mongo.get_all_contracts()
    category_list = [(i, len(app.mongo.get_contracts_by_category(i))) for i in
                     app.mongo.get_contracts_categories()]
    category_list.sort(key=lambda x: x[1], reverse=True)

    total_money = sum(map(lambda j: j['presupuesto'] if 'presupuesto' in j.keys() else 0, all_contracts))

    tweets = tw_query("comunidad madrid contrato", 20, TW_AUTH)

    return render_template(
        'index.html', numero_contratos=len(all_contracts), categorias=list(category_list),
        dinero_total=locale.format_string("%.2f", total_money, grouping=True), tweets=tweets
    )


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
    """ API NIF = B49154818
        Sandbox NIF = A46103834
    """
    # VERBOSE: Si True devuelve también los elementos que no aparecen en
    # la BBDD (Para listar todos los miembros de una empresa usar con ITERATE = False)
    VERBOSE = True

    auth = requests.auth.HTTPBasicAuth(app.config['LIBREBOR_API_USER'], app.config['LIBREBOR_API_PASS'])
    slug = request.args.get('nif')

    visited, results, iterations = librebor_find_data(app.mongo, True, slug, auth)
    if not VERBOSE:
        res = list()
        for item in results:
            if item["panama_papers"] or (item["type"] == "person" and item["electoral_lists"] is not None):
                res += [item]
        return jsonify(res)
    else:
        return jsonify(results)
