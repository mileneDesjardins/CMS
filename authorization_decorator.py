from flask import session, render_template, redirect, request
from functools import wraps

from functools import wraps
from flask import session, render_template

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'id' not in session:
            redirection = "/connexion-admin"
            if request.path == "/connexion-admin":
                redirection = "/articles"
            elif request.path == "/connexion-admin-nouveau":
                redirection = "/creation-article"
            elif request.path == "/connexion-utilisateurs":
                redirection = "/utilisateurs"
            return redirect(redirection, 302)
        return f(*args, **kwargs)
    return decorated_function

