from flask import Flask, render_template, request, redirect, g
from database import Database
import re

app = Flask(__name__, static_url_path='', static_folder='static')

# regex = r"[^A-Za-z0-9_#$]"
# mdp_existant = re.compile(regex).match(request)

@app.route('/')
def accueil():  # put application's code here
    titre = 'Accueil'
    return render_template("index.html")

def get_db():
    database = getattr(g, '_database', None)
    if database is None:
        g._database = Database()
    return g._database


def deconnection():
    database = getattr(g, '_database', None)
    if database is not None:
        database.deconnection()


def courriel_existe(courriel):
    return get_db().courriel_existe(courriel)


def valider_courriel(courriel, validation_courriel):
    return courriel == validation_courriel


# def valider_mdp(str):
#     try:
#         if mdp_existant(str) is not None:
#             return True
#     except:
#         pass
#     return False








if __name__ == '__main__':
    app.run()
