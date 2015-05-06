#This file is part ciclop blueprint for Flask.
#The COPYRIGHT file at the top level of this repository contains 
#the full copyright notices and license terms.
from flask import current_app
from trytond.config import config as tryton_config
from slug import slug
import os

def get_tryton_language(lang):
    '''
    Convert language to tryton languages
    Example: ca -> ca_ES
    '''
    languages = current_app.config.get('ACCEPT_LANGUAGES')
    for k, v in languages.iteritems():
        l = k.split('_')[0]
        if l == lang:
            return k

def get_tryton_locale(lang):
    '''
    Get locale options from lang
    '''
    languages = {
        'en': {'date': '%m/%d/%Y', 'thousands_sep': ',', 'decimal_point': '.',
            'grouping': [3, 3, 0]},
        'ca': {'date': '%d/%m/%Y', 'thousands_sep': ' ', 'decimal_point': ',',
            'grouping': [3, 3, 0]},
        'es': {'date': '%d/%m/%Y', 'thousands_sep': ',', 'decimal_point': '.',
            'grouping': [3, 3, 0]},
        'fr': {'date': '%d.%m.%Y', 'thousands_sep': ' ', 'decimal_point': ',',
            'grouping': [3, 0]},
        }
    if languages.get(lang):
        return languages.get(lang)
    return languages.get('en')

def slugify(value):
    """Convert value to slug: az09 and replace spaces by -"""
    try:
        if isinstance(value, unicode):
            name = slug(value)
        else:
            name = slug(unicode(value, 'UTF-8'))
    except:
        name = ''
    return name
