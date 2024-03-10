import hashlib
import uuid

from flask import render_template, session, redirect, request, url_for

from authorization_decorator import login_required
from database import Database
from app import app


@app.route('/creation-utilisateur', methods=['GET', 'POST'])
def creer_utilisateur():
    titre = 'Creation utilisateur'
    if request.method == "GET":
        return render_template("creation_utilisateur.html", titre=titre)
    else:
        courriel, mdp, nom, photo_data, prenom, username = (
            obtenir_infos())

        # Vérifier que les champs ne sont pas vides
        if prenom == "" or nom == "" or courriel == "" or mdp == "" or len(
                photo_data) == 0:
            return render_template("creation_utilisateur.html", titre=titre,
                                   erreur="Tous les champs sont obligatoires.")

        # Génération d'un sel et hachage du mot de passe
        mdp_salt = uuid.uuid4().hex
        mdp_hash = hashlib.sha512(
            str(mdp + mdp_salt).encode("utf-8")).hexdigest()

        # Stockage des informations de l'utilisateur (à adapter selon votre
        # base de données)
        db = Database.get_db()
        id_photo = db.create_photo(photo_data)
        db.create_user(prenom, nom, username, courriel, mdp_hash, mdp_salt,
                       id_photo)

        # Redirection vers une page de confirmation
        return redirect('/confirmation_utilisateur', 302)


def obtenir_infos():
    prenom = request.form['prenom']
    nom = request.form['nom']
    username = request.form["username"]
    courriel = request.form["courriel"]
    mdp = request.form["mdp"]
    photo = request.files["photo"]
    photo_data = photo.stream.read()
    return courriel, mdp, nom, photo_data, prenom, username


@app.route('/connexion', methods=['GET', 'POST'])
@app.route('/connexion-admin', methods=['GET', 'POST'])
@app.route('/connexion-admin-nouveau', methods=['GET', 'POST'])
@app.route('/connexion-utilisateurs', methods=['GET', 'POST'])
def connexion():
    titre = "Connexion"
    redirection = "/"
    redirection = determiner(redirection)

    if request.method == "GET":
        return render_template("connexion.html", titre=titre)
    else:
        username = request.form["username"]
        mdp = request.form["mdp"]

        if username == "" or mdp == "":
            return est_incomplet()

        utilisateur = Database.get_db().get_user_login_info(username)
        if utilisateur is None:
            return nexiste_pas()
        # Vérifier si l'utilisateur est désactivé
        if utilisateur[6] == 0:
            return est_desactive()

        mdp_hash = obtenir_mdp_hash(mdp, utilisateur)

        if mdp_hash == utilisateur[2]:
            # Accès autorisé
            return creer_session(redirection, utilisateur)
        else:
            return render_template('connexion.html',
                                   erreur="Connexion impossible, veuillez "
                                          "vérifier vos informations")


def est_incomplet():
    return render_template('connexion.html',
                           erreur="Veuillez remplir tous les champs")


def obtenir_mdp_hash(mdp, utilisateur):
    salt = utilisateur[3]
    mdp_hash = hashlib.sha512(str(mdp + salt).encode("utf-8")).hexdigest()
    return mdp_hash


def nexiste_pas():
    return render_template('connexion.html',
                           erreur="Utilisateur inexistant, veuillez "
                                  "vérifier vos informations")


def est_desactive():
    return render_template('connexion.html',
                           erreur="Connexion impossible. Votre compte "
                                  "est désactivé.")


def creer_session(redirection, utilisateur):
    id_session = uuid.uuid4().hex
    session["id"] = id_session
    session["id_utilisateur"] = utilisateur[5]
    session["prenom"] = utilisateur[0]
    session["nom"] = utilisateur[1]
    session["id_photo"] = utilisateur[4]
    return redirect(redirection, 302)


def determiner(redirection):
    if request.path == "/connexion":
        redirection = "/"
    elif request.path == "/connexion-admin":
        redirection = "/articles"
    elif request.path == "/connexion-admin-nouveau":
        redirection = "/creation-article"
    elif request.path == "/connexion-utilisateurs":
        redirection = "/utilisateurs"
    return redirection


@app.route('/deconnexion')
@login_required
def deconnexion():
    session.clear()  # Supprime toutes les données de la session
    return redirect("/")


@app.route('/modifier-utilisateur/<identifiant>', methods=['GET', 'POST'])
@login_required
def modifier_utilisateur(identifiant):
    titre = 'Modifier utilisateur'
    db = Database()

    if request.method == 'GET':
        utilisateur = db.get_user_by_id(identifiant)
        if not utilisateur:
            return render_template('404.html'), 404
        return render_template('modifier_utilisateur.html', titre=titre,
                               utilisateur=utilisateur)

    elif request.method == 'POST':
        # Récupérer les informations soumises dans le formulaire
        (nouveau_courriel, nouveau_nom, nouveau_prenom, nouveau_username,
         nouvelle_photo) = obtenir_nouvelles_infos_utilisateur()

        if not nouveau_prenom or not nouveau_nom or not nouveau_username or not nouveau_courriel:
            utilisateur = db.get_user_by_id(identifiant)
            return render_template('modifier_utilisateur.html', titre=titre,
                                   utilisateur=utilisateur,
                                   erreur="Tous les champs sont obligatoires.")

        mettre_a_jour_donnees(db, identifiant, nouveau_courriel, nouveau_nom,
                              nouveau_prenom, nouveau_username, nouvelle_photo)

        # Rediriger vers la page de tous les utilisateurs
        return redirect(url_for('utilisateurs'))


def mettre_a_jour_donnees(db, identifiant, nouveau_courriel, nouveau_nom,
                          nouveau_prenom, nouveau_username, nouvelle_photo):
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
        mettre_a_jour_photo(db, identifiant, nouvelle_photo)


def mettre_a_jour_photo(db, identifiant, nouvelle_photo):
    utilisateur = db.get_user_by_id(identifiant)
    if utilisateur:
        ancien_id_photo = utilisateur[7]
        # Supprimer l'ancienne photo
        db.delete_photo(ancien_id_photo)
        # Stocker nouvelle photo dans la BD et mettre à jour l'ID de
        # la photo de l'utilisateur
        nouveau_id_photo = db.create_photo(
            nouvelle_photo.stream.read())
        db.update_user_photo(identifiant, nouveau_id_photo)


def obtenir_nouvelles_infos_utilisateur():
    nouveau_prenom = request.form.get('prenom')
    nouveau_nom = request.form.get('nom')
    nouveau_username = request.form.get('username')
    nouveau_courriel = request.form.get('courriel')
    nouvelle_photo = request.files.get('photo')
    return (nouveau_courriel, nouveau_nom, nouveau_prenom, nouveau_username,
            nouvelle_photo)


@app.route('/desactiver-utilisateur/<identifiant>', methods=['GET', 'POST'])
@login_required
def desactiver_utilisateur(identifiant):
    db = Database()
    utilisateur = db.get_user_by_id(identifiant)

    if not utilisateur:
        return render_template('404.html'), 404
    if request.method == 'POST':
        # Vérifier si le bouton de désactivation a été cliqué
        if request.form.get('action') == 'desactiver':
            # Vérifier si l'utilisateur est actif avant de le désactiver
            etat_actif = utilisateur[8]
            if etat_actif:
                # Désactiver l'utilisateur
                db.desactiver_utilisateur(identifiant)
                return redirect(url_for('utilisateurs'))
            else:
                return redirect(url_for('utilisateurs'))
