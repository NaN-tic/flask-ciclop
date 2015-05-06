#This file is part ciclop blueprint for Flask.
#The COPYRIGHT file at the top level of this repository contains 
#the full copyright notices and license terms.
from flask import Blueprint, request, session, jsonify
from .tryton import tryton
from .helpers import login_required
from trytond.transaction import Transaction

api = Blueprint('api', __name__, template_folder='templates')

User = tryton.pool.get('res.user')

@api.route("/data", endpoint="api-data")
@login_required
@tryton.transaction()
def api_data():
    '''JSON Data'''

    def date_handler(obj):
        return obj.isoformat() if hasattr(obj, 'isoformat') else obj

    user = User(session['user'])
    model = request.args.get('model')
    domain = request.args.get('domain', [])

    with Transaction().set_user(user.id):
        try:
            Model = tryton.pool.get(model)
            vals = Model.search_read(eval(domain), fields_names=['rec_name'])
        except:
            vals = []

    return jsonify(results=vals)

@api.route("/preferences", endpoint="api-preferences")
@login_required
@tryton.transaction()
def api_preferences():
    '''JSON Preferences'''
    vals = []

    def date_handler(obj):
        return obj.isoformat() if hasattr(obj, 'isoformat') else obj

    user = User(session['user'])
    with Transaction().set_user(user.id):
        preferences = user.get_preferences()

    field = request.args.get('field')
    if field:
        if not field in preferences:
            return jsonify(results=[])
        vals = [{'id': o.id, 'rec_name': o.rec_name} \
                for o in getattr(user, field)]

    return jsonify(results=vals)
