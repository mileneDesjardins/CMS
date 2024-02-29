from flask import session, render_template, redirect, request
from functools import wraps

from functools import wraps
from flask import session, render_template

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'id' not in session:
            print(request.path)
            redirection = "/connexion"
            if request.path == "/admin":
                redirection = "/connexion-admin"
            elif request.path == "/admin-nouveau":
                redirection = "/connexion-admin-nouveau"
            elif request.path == "/utilisateurs":
                redirection = "/connexion-utilisateurs"
            return redirect(redirection, 302)
        return f(*args, **kwargs)
    return decorated_function

