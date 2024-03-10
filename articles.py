import re
import datetime

from flask import render_template, redirect, url_for, request, session

from app import app
from authorization_decorator import login_required
from database import Database


@app.route('/articles', methods=['GET'])
@login_required
def articles():
    titre = "Articles"
    # Récupérer tous les articles depuis la base de données
    db = Database.get_db()
    articles = db.get_articles()
    return render_template('articles.html', titre=titre, articles=articles)


@app.route('/article/<identifiant>', methods=['GET'])
def article(identifiant):
    titre = "Article"
    erreur = request.args.get('erreur')

    db = Database.get_db()
    article = db.get_article_by_id(identifiant)

    if article is None:
        return render_template('404.html'), 404

    utilisateur = db.get_user_by_id(article[4])
    photo = db.get_photo(utilisateur[7])

    return render_template('article.html', titre=titre,
                           article=article,
                           utilisateur=utilisateur, photo=photo, erreur=erreur)


@app.route('/modifier-article/<identifiant>', methods=['POST'])
@login_required
def modifier_article(identifiant):
    global nouveau_titre
    erreur = None

    if identifiant is None:
        return render_template('404.html'), 404

    if request.method == 'POST':
        nouveau_titre = request.form.get('nouveau_titre')
        nouveau_contenu = request.form.get('nouveau_contenu')
        id_article = request.form.get('id_article')

        # Vérifier si au moins l'un des champs est rempli
        if nouveau_titre or nouveau_contenu:
            db = Database.get_db()
            article = db.get_article_by_id(identifiant)
            if article:
                ancien_titre = article[
                    1]  # Récupérer l'ancien titre de l'article
                if nouveau_titre:
                    # Vérifier si le nouveau titre est différent de l'ancien
                    if nouveau_titre != ancien_titre:
                        # Vérifier si le nouveau titre existe déjà
                        if db.article_exists(nouveau_titre):
                            erreur = (
                                "Un article avec le même titre existe déjà. "
                                "Veuillez entrer un autre titre.")
                            return redirect(
                                url_for('article', identifiant=identifiant,
                                        erreur=erreur))
                        else:
                            # Mettre à jour le titre de l'article
                            identifiant = db.update_article_titre(
                                identifiant, nouveau_titre)

                if nouveau_contenu:
                    db.update_article_contenu(identifiant, nouveau_contenu)

    return redirect(url_for('article', identifiant=identifiant, erreur=erreur))


@app.route('/creation-article', methods=['GET', 'POST'])
@login_required
def creation_article():
    titre = 'Création article'
    date_publication = datetime.date.today()
    format_date = date_publication.strftime("%d-%m-%Y")

    if request.method == "GET":
        return render_template("creation_article.html", titre=titre,
                               titre_article="",
                               date_publication=format_date,
                               contenu="", erreur="")
    else:
        erreur = None
        contenu, date_publication, titre_article = obtenir_infos_articles()
        erreur = est_invalide(contenu, date_publication, erreur, titre_article)

        if erreur is not None:
            return afficher(contenu, date_publication, erreur, titre,
                            titre_article)

        db = Database()
        id_utilisateur = session.get('id_utilisateur')

        # Vérifier si l'id_article est déjà utilisé
        if db.article_exists(titre_article):
            return existe_deja(contenu, date_publication, titre, titre_article)

        # Créer l'article dans la base de données
        article = db.create_article(titre_article, date_publication, contenu,
                                    id_utilisateur)

        erreur = est_invalide(contenu, date_publication, erreur, titre_article)

        if erreur is not None:
            return afficher(contenu, date_publication, erreur, titre,
                            titre_article)

        return redirect(
            url_for('confirmation_article', titre_article=titre_article,
                    article=article))


def obtenir_infos_articles():
    titre_article = request.form.get('titre_article')
    date_publication = request.form.get('date_publication')
    contenu = request.form.get('contenu')
    return contenu, date_publication, titre_article


def afficher(contenu, date_publication, erreur, titre, titre_article):
    return render_template("creation_article.html",
                           titre=titre,
                           titre_article=titre_article,
                           date_publication=date_publication,
                           contenu=contenu, erreur=erreur)


def existe_deja(contenu, date_publication, titre, titre_article):
    erreur = ("Un article avec le même titre existe déjà. Veuillez "
              "en choisir un autre.")
    return render_template("creation_article.html", titre=titre,
                           titre_article=titre_article,
                           date_publication=date_publication,
                           contenu=contenu,
                           erreur=erreur)


def est_invalide(contenu, date_publication, erreur, titre_article):
    # Vérifier si l'un des champs est vide
    if not titre_article or not date_publication or not contenu:
        erreur = "Veuillez remplir tous les champs."
    # Vérifier si le titre a au moins 3 caractères
    if len(titre_article) < 3:
        erreur = "Le titre doit avoir au moins 3 lettres."
    # Vérifier si le champ titre dépasse 100 caractères
    if len(titre_article) > 100:
        erreur = "Le titre doit avoir moins de 100 lettres."
    # Vérifier si le format de la date est valide
    if not re.match(r'^\d{2}-\d{2}-\d{4}$', date_publication):
        erreur = ("Le format de la date de publication n'est pas valide. "
                  "Utilisez le format DD-MM-YYYY.")
    # Vérifier si le contenu a au moins 15 mots
    if len(contenu.split()) < 30:
        erreur = "Le contenu doit avoir au moins 15 mots."
    # Vérifier si le contenu a plus de 200 mots
    if len(contenu.split()) > 200:
        erreur = "Le contenu doit avoir moins de 200 mots."
    return erreur


@app.route('/supprimer-article/<identifiant>', methods=['POST'])
@login_required
def supprimer_article(identifiant):
    if identifiant is None:
        return render_template('404.html'), 404

    if request.method == 'POST':
        db = Database.get_db()
        db.delete_article(identifiant)
    return redirect(url_for('articles'))
