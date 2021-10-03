import simplejson as json

from flask import (Blueprint, flash, render_template, make_response, session,
                   request, current_app as app, url_for, abort, redirect)
from src.models import db, Contrato

main_module = Blueprint('main', __name__, template_folder='../templates')
