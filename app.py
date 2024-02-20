import hashlib
import sqlite3
import uuid

from flask import Flask, render_template, request, redirect, g, session, url_for

from authorization_decorator import login_required
from database import Database
import re

app = Flask(__name__, static_url_path='', static_folder='static')


# regex = r"[^A-Za-z0-9_#$]"
# mdp_existant = re.compile(regex).match(request)

@app.route('/')
def accueil():  # put application's code here
    titre = 'Accueil'
    prenom = session.get('prenom')
    nom = session.get('nom')
    if prenom and nom:
        return render_template('index.html', titre=titre, prenom=prenom, nom=nom)
    else:
        return render_template("index.html", titre=titre)

@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    titre = 'Inscription'
    if request.method == "GET":
        return render_template("incription.html")
    else:
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]

        # Vérifier que les champs ne sont pas vides
        if username == "" or password == "" or email == "":
            return render_template("inscription.html", titre=titre, error="Tous les champs sont obligatoires.")

        # Validation du formulaire - Vous pouvez implémenter votre propre logique de validation ici

        # Génération d'un sel et hachage du mot de passe
        salt = uuid.uuid4().hex
        hashed_password = hashlib.sha512(str(password + salt).encode("utf-8")).hexdigest()


        # Stockage des informations de l'utilisateur (à adapter selon votre base de données)
        # Exemple : sauvegarde dans une base de données
        # db.create_user(username, email, salt, hashed_password)
        db = get_db()
        db.create_user(username, email, salt, hashed_password)

        # Redirection vers une page de confirmation
        return redirect(url_for('confirmation'), 302)




@app.route('/connection', methods=['GET', 'POST'])
def connection():
    titre = "Connection"
    return render_template("connection.html", titre=titre)


@app.route('/deconnexion', methods=['GET', 'POST'])

@app.route("/confirmation")
def conirmation():
    title = "Pis moe - Vous etes inscrit"
    prenom = request.args.get('prenom')
    return render_template('confirmation.html', title=title)

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    Titre = "Admin"


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
