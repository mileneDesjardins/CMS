import datetime
import hashlib
import uuid
from functools import wraps
import os
from dotenv import load_dotenv

from flask import Flask, render_template, request, redirect, g, session, Response, url_for

from authorization_decorator import login_required
from database import Database

load_dotenv()
app = Flask(__name__, static_url_path='', static_folder='static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


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


# regex = r"[^A-Za-z0-9_#$]"
# mdp_existant = re.compile(regex).match(request)

@app.route('/', methods=['GET'])
def accueil():
    titre = 'Accueil'
    if "id" in session:
        prenom = session.get('prenom')
        nom = session.get('nom')
        photo = get_db().get_photo(session["id_photo"])
    else:
        prenom = None
        nom = None
        photo = None
    return render_template('index.html', titre=titre, prenom=prenom, nom=nom, photo=photo)



@app.route('/recherche', methods=['GET', 'POST'])
def recherche():
    if request.method == 'POST':
        recherche_input = request.form["recherche_input"]
        if not recherche_input:
            return redirect('/'), 302
        else:
            db = get_db()
            articles = db.get_articles(recherche_input)
            return redirect(url_for('/resultats', query=recherche_input, articles=articles)), 302
    elif request.method == 'GET':
        return render_template("index.html")


@app.route('/resultats/<query>', methods=['GET', 'POST'])
def resultats(query):
    articles = request.args.get('articles', [])
    return render_template('resultats.html', query=query, articles=articles)


@app.route('/creation_utilisateur', methods=['GET', 'POST'])
def inscription():
    titre = 'Inscription'
    if request.method == "GET":
        return render_template("creation_utilisateur.html")
    else:
        prenom = request.form['prenom']
        nom = request.form['nom']
        username = request.form["username"]
        courriel = request.form["courriel"]
        mdp = request.form["mdp"]
        photo = request.files["photo"]
        photo_data = photo.stream.read()

        # Vérifier que les champs ne sont pas vides
        if prenom == "" or nom == "" or courriel == "" or mdp == "" or len(photo_data) == 0:
            return render_template("creation_utilisateur.html", titre=titre,
                                   erreur="Tous les champs sont obligatoires.")

        # Validation du formulaire - Vous pouvez implémenter votre propre logique de validation ici

        # Génération d'un sel et hachage du mot de passe
        mdp_salt = uuid.uuid4().hex
        mdp_hash = hashlib.sha512(str(mdp + mdp_salt).encode("utf-8")).hexdigest()

        # Stockage des informations de l'utilisateur (à adapter selon votre base de données)
        db = get_db()
        id_photo = db.create_photo(photo_data)

        db.create_user(prenom, nom, username, courriel, mdp_hash, mdp_salt, id_photo)

        # Redirection vers une page de confirmation
        return redirect('/confirmation', 302)


@app.route('/connexion', methods=['GET', 'POST'])
@app.route('/connexion-admin', methods=['GET', 'POST'])
@app.route('/connexion-admin-nouveau', methods=['GET', 'POST'])
@app.route('/connexion-utilisateurs', methods=['GET', 'POST'])
def connexion():
    titre = "Connexion"
    redirection = "/"

    if request.path == "/connexion-admin":
        redirection = "/articles"
    elif request.path == "/connexion-admin-nouveau":
        redirection = "/creation-article"
    elif request.path == "/connexion-utilisateurs":
        redirection = "/utilisateurs"

    if request.method == "GET":
        return render_template("connexion.html", titre=titre)
    else:
        username = request.form["username"]
        mdp = request.form["mdp"]

        if username == "" or mdp == "":
            return render_template('connexion.html', erreur="Veuillez remplir tous les champs")

        utilisateur = get_db().get_user_login_info(username)
        if utilisateur is None:
            return render_template('connexion.html',
                                   erreur="Utilisateur inexistant, veuillez vérifier vos informations")

        salt = utilisateur[3]
        mdp_hash = hashlib.sha512(str(mdp + salt).encode("utf-8")).hexdigest()
        if mdp_hash == utilisateur[2]:
            # Accès autorisé
            id_session = uuid.uuid4().hex
            # get_db().save_session(id_session, username)

            session["id"] = id_session
            session["prenom"] = utilisateur[0]
            session["nom"] = utilisateur[1]
            session["id_photo"] = utilisateur[4]
            return redirect(redirection, 302)

        else:
            return render_template('connexion.html', erreur="Connexion impossible, veuillez vérifier vos informations")


@app.route('/deconnexion')
@login_required
def deconnexion():
    session.clear()  # Supprime toutes les données de la session
    return redirect("/")

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    titre = "Articles"
    return render_template('articles.html', titre=titre)

@app.route('/admin-nouveau', methods=['GET', 'POST'])
@login_required
def creation_article():
    date = datetime.date.today()
    # Formater la date au format DD-MM-YYYY
    format_date = date.strftime("%d-%m-%Y")

    titre = 'Création article'
    if request.method == "GET":
        return render_template("creation_article.html", date=format_date)
    else:
        # Rendre le modèle index.html en passant la date formatée
        return redirect('/confirmation', 302)

@app.route('/utilisateurs', methods=['GET'])
@login_required
def utilisateurs():
    titre = 'Utilisateurs'
    return render_template('utilisateurs.html', titre=titre)

@app.route('/confirmation', methods=['GET'])
def confirmation():
    return render_template('confirmation.html')


if __name__ == '__main__':
    app.run()
