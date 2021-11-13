from flask import (
    Blueprint, flash, render_template, make_response, session,
    request, current_app as app, url_for, abort, redirect
)
import locale

import json

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

    return render_template('index.html', numero_contratos=len(all_contracts),
                           categorias=list(category_list), dinero_total=locale.format_string("%.2f",total_money,grouping=True))

@main_module.route('/results', methods=['POST'])
def results():
    """ Aquí se llega desde el index al realizar una búsqueda.
        Se muestra el listado de contrataciones

        REFERENCIA DE QUÉ NECESITO EN EL FRONT: https://github.com/Patataman/DMyE1/issues/10
    """
    busqueda = request.form['busqueda']
    print(busqueda)
    search = app.mongo.get_contracts_by_title(busqueda)
    print(search)
    return render_template('results.html', busqueda=busqueda, contratos=search)
