from flask import (Blueprint, flash, render_template, make_response, session,
                   request, current_app as app, url_for, abort, redirect)
from src.models import db #, Contrato

import json

main_module = Blueprint('main', __name__, template_folder='../templates')


@main_module.route('/', methods=['GET'])
def index():
    return render_template('index.html')
