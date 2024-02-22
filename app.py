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
    if "id" in session:
        prenom = get_db().get_session(session["prenom"])
        nom = get_db().get_session(session["nom"])
        return render_template('index.html', titre=titre, prenom=prenom, nom=nom)
    else:
        return render_template("index.html", titre=titre)


@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    titre = 'Inscription'
    if request.method == "GET":
        return render_template("inscription.html")
    else:
        prenom = request.form['prenom']
        nom = request.form['nom']
        courriel = request.form["courriel"]
        mdp = request.form["mdp"]
        photo = request.files["photo"]
        photo_data = photo.stream.read()

        # Vérifier que les champs ne sont pas vides
        if prenom == "" or nom == "" or courriel == "" or mdp == "" or len(photo_data) == 0:
            return render_template("inscription.html", titre=titre, erreur="Tous les champs sont obligatoires.")

        # Validation du formulaire - Vous pouvez implémenter votre propre logique de validation ici

        # Génération d'un sel et hachage du mot de passe
        mot_de_passe_salt = uuid.uuid4().hex
        mot_de_passe_hash = hashlib.sha512(str(mdp + mot_de_passe_salt).encode("utf-8")).hexdigest()

        # Stockage des informations de l'utilisateur (à adapter selon votre base de données)
        db = get_db()
        id_photo = db.create_photo(photo_data)
        db.create_user(prenom, nom, courriel, mot_de_passe_salt, mot_de_passe_hash, id_photo)

        # Redirection vers une page de confirmation
        return redirect(url_for('confirmation'), 302)


@app.route('/connexion', methods=['GET', 'POST'])
def connexion():
    titre = "Connexion"

    if request.method == 'POST':
        courriel = request.form["courriel"]
        mdp = request.form["mdp"]

        #SQLite
        connection = sqlite3.connect('utilisateur.db')
        cursor = connection.cursor()
        cursor.execute(("select salt, hash from utilisateur where utilisateur=?"),
                       (courriel,))
        utilisateur = cursor.fetchone()
        connection.close()


        courriel = request.form["courriel"]
        mdp = request.form["mdp"]



    if courriel is None:
        print("Utilisateur inconnu")
    else:
        salt = utilisateur[0]
        hashed_password = hashlib.sha512(str(mdp + salt).encode("utf-8")).hexdigest()
        if hashed_password == utilisateur[1]:
            # ouvrir session

            return render_template("index.html", titre=titre, prenom=prenom, nom=nom)
        else:
            return render_template("connexion.html", titre=titre, erreur="Les informations sont invalides")


@app.route("/confirmation")
def confirmation():
    title = "Pis moe - Vous etes inscrit"
    prenom = request.args.get('prenom')
    nom = request.args.get('nom')
    return render_template('index.html', title=title, prenom=prenom, nom=nom)


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    Titre = "Admin"


def get_db():
    database = getattr(g, '_database', None)
    if database is None:
        g._database = Database()
    return g._database


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.disconnect()


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
