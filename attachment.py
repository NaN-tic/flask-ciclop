#This file is part ciclop blueprint for Flask.
#The COPYRIGHT file at the top level of this repository contains 
#the full copyright notices and license terms.
from flask import Blueprint, current_app, abort, send_file
from .tryton import tryton
from .helpers import login_required
import ConfigParser
import os
import magic

attachment = Blueprint('attachment', __name__, template_folder='templates')
Config = ConfigParser.ConfigParser()
tryton_config = current_app.config.get('TRYTON_CONFIG')
Config.readfp(open(tryton_config))

DATA = Config.get('database', 'path')
DATABASE = current_app.config.get('TRYTON_DATABASE')

@attachment.route('/file/<path:filename>', endpoint="file")
@login_required
@tryton.transaction()
def filename(filename):
    '''File Attachment'''

    attach = '%s/%s/%s/%s/%s' % (
        DATA,
        DATABASE,
        filename[:2],
        filename[2:4:],
        filename,
        )
    if not os.path.isfile(attach):
        abort(404)

    mimetype = magic.from_file(attach, mime=True)
    return send_file(attach, mimetype=mimetype)
