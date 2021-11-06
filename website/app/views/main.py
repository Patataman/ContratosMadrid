from flask import (
    Blueprint, flash, render_template, make_response, session,
    request, current_app as app, url_for, abort, redirect
)

import json

main_module = Blueprint('main', __name__, template_folder='../templates')


@main_module.route('/', methods=['GET'])
def index():
    """ Página principal
    """
    return render_template('index.html')


@main_module.route('/results', methods=['POST'])
def results():
    """ Aquí se llega desde el index al realizar una búsqueda.
        Se muestra el listado de contrataciones

        REFERENCIA DE QUÉ NECESITO EN EL FRONT: https://github.com/Patataman/DMyE1/issues/10
    """
    busqueda = request.form['busqueda']
    return render_template('results.html', busqueda=busqueda, contratos=[1]*30)
