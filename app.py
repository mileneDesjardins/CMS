import hashlib
import uuid
from functools import wraps

from flask import Flask, render_template, request, redirect, g, session, url_for, Response

from authorization_decorator import login_required
from database import Database

app = Flask(__name__, static_url_path='', static_folder='static')

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


@app.route('/connexion', methods=['POST'])
def connexion():
    titre = "Connexion"
    courriel = request.form["courriel"]
    mdp = request.form["mdp"]

    if courriel == "" or mdp == "":
        # TODO Faire la gestion de l'erreur
        return redirect(url_for('connexion', erreur="Veuillez remplir tous les champs"), 302)

    utilisateur = get_db().get_user_login_info(courriel)
    if utilisateur is None:
        # TODO Faire la gestion de l'erreur
        return redirect(url_for("/connexion", titre=titre, erreur="Utilisateur inexistant, veuillez vérifier vos informations ou créer un nouveau compte."), 302)

    salt = utilisateur[0]
    mdp_hash = hashlib.sha512(str(mdp + salt).encode("utf-8")).hexdigest()
    if mdp_hash == utilisateur[1]:
        # ouvrir session
        # Accès autorisé
        id_session = uuid.uuid4().hex
        get_db().save_session(id_session, courriel)
        prenom = session.get("prenom")
        nom = session.get("nom")
        return redirect(url_for("/accueil", titre=titre, prenom=prenom, nom=nom), 302)
    else:
        # TODO Faire la gestion de l'erreur
        return redirect(url_for("/connexion", titre=titre, erreur="Connexion impossible, veuillez vérifier vos informations."), 302)

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





if __name__ == '__main__':
    app.run()
