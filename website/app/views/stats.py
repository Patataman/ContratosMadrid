from app.views.utils import librebor_find_data, tw_auth, tw_query
from collections import defaultdict
from flask import (
    Blueprint, flash, render_template, make_response, session,
    request, jsonify, current_app as app, url_for, abort, redirect
)
from tempfile import NamedTemporaryFile

import json
import plotly.graph_objects as go
import time


stats_module = Blueprint('stats', __name__, template_folder='../templates')


@stats_module.route('/', methods=['GET'])
def stats():
    """ Página de estadísticas
    """

    # Contratos por categoría
    t0 = time.time()
    contratos_por_cat = {
        i: app.mongo.get_contracts_by_category(i).count()
        for i in app.mongo.get_contracts_categories()
    }
    contratos_cat_fig = go.Figure(
        data=[
            go.Pie(
                labels=[k for k in contratos_por_cat.keys()],
                values=[v for v in contratos_por_cat.values()],
                textinfo='label+percent',
                textposition="none",
                insidetextorientation='radial',
            )
        ]
    )
    contratos_por_cat['total'] = app.mongo.get_all_contracts().count()
    print("Contratos", round(time.time() - t0, 4))

    contratos_cat_html = ""
    with NamedTemporaryFile() as tmp:
        contratos_cat_fig.write_html(
            tmp.name,
            full_html=False,
            include_plotlyjs=False
        )
        tmp.seek(0)
        contratos_cat_html = tmp.read().decode("utf-8")
    ##########################

    # Contratos por empresa
    empresas = app.mongo.unique_company()

    t0 = time.time()
    # https://stackoverflow.com/questions/16789369/mongodb-group-by-key
    top_nifs = app.mongo.get_aggregate_contracts([
        {"$match": {"adjudicacion": { "$exists" : True }}},
        {"$group": {
            "_id": "$adjudicacion.nif adjudicatario",
            "count": { "$sum": 1 }}
        },
        {"$sort":{"count":-1}},
    ])
    # Convierte esto en un diccionario para agilizar búsqueda
    top_nifs = {d['_id']: d['count'] for d in top_nifs}

    contratos_por_empresa = {
        doc['document']['name']: top_nifs[doc['_id']]
        for doc in empresas
    }
    # Ordenamos de más o menos
    contratos_por_empresa = dict(
        sorted(contratos_por_empresa.items(), key=lambda item: item[1], reverse=True)
    )

    print("Empresas", round(time.time() - t0, 4))

    contratos_comp_fig = go.Figure(
        data=[
            go.Pie(
                labels=[k for k in contratos_por_empresa.keys()],
                values=[v for v in contratos_por_empresa.values()],
                textinfo='label+percent',
                textposition="none",
                insidetextorientation='radial',
            )
        ]
    )

    contratos_empresa_html = ""
    with NamedTemporaryFile() as tmp:
        contratos_comp_fig.write_html(
            tmp.name,
            full_html=False,
            include_plotlyjs=False
        )
        tmp.seek(0)
        contratos_empresa_html = tmp.read().decode("utf-8")
    ##########################

    # Anomalías
    t0 = time.time()
    print("Anomalias", round(time.time() - t0, 4))

    #########################

    return render_template(
        'stats.html',
        contratos_por_cat=contratos_por_cat,
        contratos_por_cat_fig=contratos_cat_html,
        contratos_por_empresa=contratos_por_empresa,
        contratos_por_empresa_fig=contratos_empresa_html,
        anomalias=[],
        anomalias_fig=""
    )
