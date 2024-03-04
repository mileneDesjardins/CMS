import datetime
import hashlib
import uuid
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, g, session, Response, url_for, jsonify, flash
import re

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


@app.route('/', methods=['GET'])
def accueil():
    titre = 'Accueil'
    if "id" in session:
        prenom = session.get('prenom')
        nom = session.get('nom')
    else:
        prenom = None
        nom = None

    db = get_db()
    articles = db.get_cinq_dernier_articles()

    id_utilisateurs = [article[4] for article in
                       articles]  # Liste des ID utilisateur du cinquième élément de chaque article

    utilisateurs = [db.get_user_by_id(id_utilisateur) for id_utilisateur in
                    id_utilisateurs]  # Liste des informations des utilisateurs

    photos = [db.get_photo(utilisateur[7]) for utilisateur in utilisateurs]

    return render_template('index.html', titre=titre, prenom=prenom, photos=photos, nom=nom, articles=articles,
                           utilisateurs=utilisateurs)


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

    if request.path == "/connexion":
        redirection = "/"
    elif request.path == "/connexion-admin":
        redirection = "/articles"
    elif request.path == "/connexion-admin-nouveau":
        redirection = "/creation_article"
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

        # Vérifier si l'utilisateur est désactivé
        if utilisateur[6] == 0:
            return render_template('connexion.html', erreur="Connexion impossible. Votre compte est désactivé.")

        salt = utilisateur[3]
        mdp_hash = hashlib.sha512(str(mdp + salt).encode("utf-8")).hexdigest()
        if mdp_hash == utilisateur[2]:
            # Accès autorisé
            id_session = uuid.uuid4().hex
            # get_db().save_session(id_session, username)

            session["id"] = id_session
            session["id_utilisateur"] = utilisateur[5]
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


@app.route('/admin', methods=['GET'])
@login_required
def admin():
    titre = "Articles"
    # Récupérer tous les articles depuis la base de données
    return render_template('articles.html', titre=titre, articles=articles)


@app.route('/articles', methods=['GET'])
@login_required
def articles():
    titre = "Articles"
    # Récupérer tous les articles depuis la base de données
    db = get_db()
    articles = db.get_articles()  # Utilisez la fonction pour récupérer tous les articles
    return render_template('articles.html', titre=titre, articles=articles)


@app.route('/article/<identifiant>', methods=['GET'])
def article(identifiant):
    titre = "Article"
    photo = get_db().get_photo(session["id_photo"])

    db = get_db()
    article = db.get_article_by_id(identifiant)  # Récupérer un article par son ID

    if article is None:
        return render_template('404.html'), 404

    utilisateur = db.get_user_by_id(article[4])
    return render_template('article.html', titre=titre, article=article,
                           utilisateur=utilisateur, photo=photo)


@app.route('/modifier-article/<identifiant>', methods=['POST'])
@login_required
def modifier_article(identifiant):
    if request.method == 'POST':
        nouveau_titre = request.form.get('nouveau_titre')
        nouveau_contenu = request.form.get('nouveau_contenu')
        id_article = request.form.get('id_article')

        # Vérifier si au moins l'un des champs est rempli
        if nouveau_titre or nouveau_contenu:
            db = get_db()
            article = db.get_article_by_id(identifiant)
            if article:
                if nouveau_titre:
                    db.update_article_titre(identifiant, nouveau_titre)
                if nouveau_contenu:
                    db.update_article_contenu(identifiant, nouveau_contenu)
                flash('Article modifié avec succès.', 'success')
            else:
                flash('Article non trouvé.', 'error')
        else:
            flash('Le nouveau titre ou le nouveau contenu est obligatoire.', 'error')
    return redirect(url_for('article', identifiant=identifiant))


@app.route('/photo/<id_photo>')
def photo(id_photo):
    photo_data = get_db().get_photo(id_photo)
    if photo_data:
        return Response(photo_data, mimetype='application/octet-stream')


@app.route('/admin-nouveau', methods=['GET', 'POST'])
@login_required
def admin_nouveau():
    titre = "Création article"
    # Récupérer tous les articles depuis la base de données
    return render_template('creation_article.html', titre=titre)


@app.route('/creation-article', methods=['GET', 'POST'])
@login_required
def creation_article():
    date_publication = datetime.date.today()
    # Formater la date au format DD-MM-YYYY
    format_date = date_publication.strftime("%d-%m-%Y")

    titre = 'Création article'

    if request.method == "GET":
        return render_template("creation_article.html", titre=titre, titre_article="",
                               date_publication=format_date,
                               contenu="", erreur="")
    else:
        # Récupérer les données du formulaire
        titre_article = request.form.get('titre_article')
        date_publication = request.form.get('date_publication')
        contenu = request.form.get('contenu')

        # Vérifier si l'un des champs est vide
        if not titre_article or not date_publication or not contenu:
            erreur = "Veuillez remplir tous les champs."
            return render_template("creation_article.html", titre=titre, titre_article=titre_article,
                                   date_publication=date_publication, contenu=contenu, erreur=erreur)

        # Vérifier si le titre a au moins 3 caractères
        if len(titre_article) < 3:
            erreur = "Le titre doit avoir au moins 3 caractères."
            return render_template("creation_article.html", titre=titre, titre_article=titre_article,
                                   date_publication=date_publication, contenu=contenu,
                                   erreur=erreur)

        # Vérifier si le champ titre dépasse 100 caractères
        if len(titre_article) > 100:
            erreur = "Le titre ne doit pas dépasser 100 caractères."
            return render_template("creation_article.html", titre=titre, titre_article=titre_article,
                                   date_publication=date_publication, contenu=contenu,
                                   erreur=erreur)

        # Vérifier si le format de la date est valide
        if not re.match(r'^\d{2}-\d{2}-\d{4}$', date_publication):
            erreur = "Le format de la date de publication n'est pas valide. Utilisez le format DD-MM-YYYY."
            return render_template("creation_article.html", titre=titre, titre_article=titre_article,
                                   date_publication=date_publication, contenu=contenu,
                                   erreur=erreur)

        # Vérifier si le contenu a au moins 15 caractères
        if len(contenu) < 15:
            erreur = "Le contenu doit avoir au moins 15 caractères."
            return render_template("creation_article.html", titre=titre, titre_article=titre_article,
                                   date_publication=date_publication, contenu=contenu,
                                   erreur=erreur)

        # Insérer l'article dans la base de données
        db = Database()
        id_utilisateur = session.get('id_utilisateur')
        article = db.create_article(titre_article, date_publication, contenu, id_utilisateur)

        # Rediriger vers une page de confirmation avec l'ID de l'article créé
        return redirect(url_for('confirmation_article', titre_article=titre_article, article=article))


@app.route('/utilisateurs', methods=['GET', "POST"])
@login_required
def utilisateurs():
    titre = 'Utilisateurs'
    db = Database()
    utilisateurs = db.get_all_users()
    return render_template('utilisateurs.html', titre=titre, utilisateurs=utilisateurs)


@app.route('/modifier-utilisateur/<identifiant>', methods=['GET', 'POST'])
@login_required
def modifier_utilisateur(identifiant):
    titre = 'Modifier utilisateur'
    db = Database()

    if request.method == 'GET':
        # Récupérer les informations de l'utilisateur
        utilisateur = db.get_user_by_id(identifiant)
        if not utilisateur:
            return render_template('404.html'), 404
        return render_template('modifier_utilisateur.html', titre=titre, utilisateur=utilisateur)

    elif request.method == 'POST':
        # Récupérer les informations soumises dans le formulaire
        nouveau_prenom = request.form.get('prenom')
        nouveau_nom = request.form.get('nom')
        nouveau_username = request.form.get('username')
        nouveau_courriel = request.form.get('courriel')
        nouvelle_photo = request.files.get('photo')

        # Mettre à jour les champs si les nouvelles valeurs sont fournies
        if nouveau_prenom:
            db.update_user_prenom(identifiant, nouveau_prenom)
        if nouveau_nom:
            db.update_user_nom(identifiant, nouveau_nom)
        if nouveau_username:
            db.update_user_username(identifiant, nouveau_username)
        if nouveau_courriel:
            db.update_user_courriel(identifiant, nouveau_courriel)
        if nouvelle_photo:
            # Stocker la nouvelle photo dans la base de données et mettre à jour l'ID de la photo de l'utilisateur
            nouveau_id_photo = db.create_photo(nouvelle_photo.stream.read())
            db.update_user_photo(identifiant, nouveau_id_photo)

        # Rediriger vers la page de tous les utilisateurs
        return redirect(url_for('utilisateurs'))


@app.route('/desactiver-utilisateur/<identifiant>', methods=['GET', 'POST'])
@login_required
def desactiver_utilisateur(identifiant):
    db = Database()

    if request.method == 'POST':
        # Vérifier si le bouton de désactivation a été cliqué
        if request.form.get('action') == 'desactiver':
            # Récupérer les informations sur l'utilisateur
            utilisateur = db.get_user_by_id(identifiant)
            if not utilisateur:
                return render_template('404.html'), 404
            # Vérifier si l'utilisateur est actif avant de le désactiver
            etat_actif = utilisateur[8]  # Supposons que le dernier élément est l'état d'activation
            if etat_actif:
                # Désactiver l'utilisateur
                db.desactiver_utilisateur(identifiant)
                # Rediriger vers une page de confirmation ou une autre vue
                return redirect(url_for('utilisateurs'))

    # Récupérer les informations sur l'utilisateur
    utilisateur = db.get_user_by_id(identifiant)
    if not utilisateur:
        return render_template('404.html'), 404

    return render_template('utilisateurs.html', utilisateur=utilisateur)


@app.route('/confirmation', methods=['GET'])
def confirmation():
    return render_template('confirmation.html')


@app.route('/confirmation_article', methods=['GET'])
def confirmation_article():
    titre = "Création réussie"
    titre_article = request.args.get('titre_article')
    return render_template('confirmation_article.html', titre=titre, titre_article=titre_article)


if __name__ == '__main__':
    app.run()
