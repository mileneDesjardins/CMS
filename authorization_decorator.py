from flask import session, render_template
from functools import wraps

from functools import wraps
from flask import session, render_template

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'id' not in session:
            return render_template('index.html', message="Veuillez vous connecter pour accéder à cette page.")
        return f(*args, **kwargs)
    return decorated_function
