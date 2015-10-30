#This file is part ciclop blueprint for Flask.
#The COPYRIGHT file at the top level of this repository contains 
#the full copyright notices and license terms.
from flask import Blueprint, request, render_template, current_app, session, \
    redirect, url_for, flash, g
from flask.ext.babel import gettext as _
from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, validators
from .tryton import tryton
from .signals import login as slogin, failed_login as sfailed_login, logout as slogout
from .helpers import login_required
from .csrf import csrf
from trytond.transaction import Transaction

ciclop = Blueprint('ciclop', __name__, template_folder='templates')

REDIRECT_AFTER_LOGIN = current_app.config.get('REDIRECT_AFTER_LOGIN')
REDIRECT_AFTER_LOGOUT = current_app.config.get('REDIRECT_AFTER_LOGOUT')
LOGIN_EXTRA_FIELDS = current_app.config.get('LOGIN_EXTRA_FIELDS', [])

User = tryton.pool.get('res.user')

class LoginForm(Form):
    "Login form"
    login = TextField(_('Login'), [validators.Required()])
    password = PasswordField(_('Password'), [validators.Required()])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        return True


@ciclop.route("/login", methods=["GET", "POST"], endpoint="login")
@tryton.transaction()
def login(lang):
    '''Login App'''
    data = {}

    form = LoginForm()
    if form.validate_on_submit():
        login = request.form.get('login')
        password = request.form.get('password')

        user_id = User.get_login(login, password)
        if user_id:
            user = User(user_id)
            session['logged_in'] = True
            session['user'] = user_id
            session['name'] = user.name
            session['email'] = user.email
            for field in LOGIN_EXTRA_FIELDS: # add extra fields in session
                f = getattr(user, field)
                if hasattr(f, 'id'): # can not save an object in session
                    f = getattr(f, 'id') 
                session[field] = f

            flash(_('You are logged in'))
            slogin.send(current_app._get_current_object(),
                user=user['id'],
                session=session.sid,
                )
            if request.form.get('redirect'):
                path_redirect = request.form['redirect']
                if not path_redirect[:4] == 'http':
                    return redirect(path_redirect)

            if user.language and user.language.code in current_app.config.get('ACCEPT_LANGUAGES', []):
                language = user.language.code[:2]
            else:
                language = g.language
            if REDIRECT_AFTER_LOGIN:
                return redirect(url_for(REDIRECT_AFTER_LOGIN, lang=language))
            else:
                return redirect(url_for(language))
        else:
            flash(_("Could not authenticate you."), 'danger')

        data['login'] = login
        sfailed_login.send(form=form)

    return render_template('login.html', form=form, data=data)

@ciclop.route('/logout', endpoint="logout")
@login_required
@tryton.transaction()
def logout(lang):
    '''Logout App'''
    user = session.get('user')

    # Remove all sessions
    session.pop('logged_in', None)
    session.pop('user', None)
    session.pop('name', None)
    session.pop('email', None)

    for field in LOGIN_EXTRA_FIELDS: # drop extra session fields
         session.pop(field, None)

    slogout.send(current_app._get_current_object(),
        user=user,
        )

    flash(_('You are logged out.'))
    if REDIRECT_AFTER_LOGOUT:
        return redirect(url_for(REDIRECT_AFTER_LOGOUT, lang=g.language))
    else:
        return redirect(url_for(g.language))

@ciclop.route('/profile', methods=["GET", "POST"], endpoint="profile")
@login_required
@tryton.transaction()
@csrf.exempt
def profile(lang):
    '''User Preferences App'''
    user = User(session['user'])

    if request.method == 'POST':
        vals = dict((k, v) for (k, v) in request.form.iteritems() if v)
        with Transaction().set_user(user.id):
            user.set_preferences(vals)
    preferences = user.get_preferences()

    #breadcumbs
    breadcrumbs = [{
        'slug': url_for('.profile', lang=g.language),
        'name': _('User'),
        }]

    return render_template('user-profile.html',
        breadcrumbs=breadcrumbs,
        preferences=preferences,
        user=user,
        )
