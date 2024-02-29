from flask import session, render_template, redirect
from functools import wraps

from functools import wraps
from flask import session, render_template

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'id' not in session:
            return redirect('/connexion_admin', 302)
        return f(*args, **kwargs)
    return decorated_function
