import hashlib
import uuid
from functools import wraps
import os
from dotenv import load_dotenv

from flask import Flask, render_template, request, redirect, g, session, url_for, Response

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

@app.route('/')
def accueil():  # put application's code here
    titre = 'Accueil'
    if "id" in session:
        prenom = session["prenom"]
        nom = session["nom"]
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
        return redirect('/confirmation', 302)


@app.route('/connexion', methods=['GET', 'POST'])
def connexion():
    titre = "Connexion"

    if request.method == "GET":
        return render_template("connexion.html")
    else:
        courriel = request.form["courriel"]
        mdp = request.form["mdp"]

        if courriel == "" or mdp == "":
            # TODO Faire la gestion de l'erreur
            return render_template('connexion.html', erreur="Veuillez remplir tous les champs")

        utilisateur = get_db().get_user_login_info(courriel)
        if utilisateur is None:
            # TODO Faire la gestion de l'erreur
            return render_template('connexion.html', erreur="Utilisateur inexistant, veuillez vérifier vos informations ou créer un nouveau compte")

        salt = utilisateur[0]
        mdp_hash = hashlib.sha512(str(mdp + salt).encode("utf-8")).hexdigest()
        if mdp_hash == utilisateur[1]:
            # Accès autorisé
            id_session = uuid.uuid4().hex
            get_db().save_session(id_session, courriel)

            session["id"] = id_session

            session["prenom"] = utilisateur[2]
            session["nom"] = utilisateur[3]
            return redirect("/"), 302
        else:
            # TODO Faire la gestion de l'erreur
            return render_template('connexion.html', erreur="Connexion impossible, veuillez vérifier vos informations")

def authentication_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not is_authenticated(session):
            return send_unauthorized()
        return f(*args, **kwargs)
    return decorated

@app.route('/deconnexion')
@authentication_required
def logout():
    id_session = session["id"]
    session.pop('id', None)
    get_db().delete_session(id_session)
    return redirect("/")

def is_authenticated(session):
    # TODO Next-level : Vérifier la session dans la base de données
    return "id" in session

def send_unauthorized():
    return Response('Could not verify your access level for that URL.\n'
                    'You have to login with proper credentials.', 401,
                    {'WWW-Authenticate': 'Basic realm="Login Required"'})

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    Titre = "Admin"

@app.route('/confirmation', methods=['GET'])
def confirmation():
    return render_template('confirmation.html')

if __name__ == '__main__':
    app.run()
