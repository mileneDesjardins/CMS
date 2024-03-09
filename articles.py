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
    article = db.get_article_by_id(
        identifiant)  # Récupérer un article par son ID
    photo = db.get_photo(article[4])

    if article is None:
        return render_template('404.html'), 404

    utilisateur = db.get_user_by_id(article[4])
    return render_template('article.html', titre=titre, article=article,
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
                if nouveau_titre:
                    # Vérifier si le nouveau titre existe déjà
                    if db.article_exists(nouveau_titre):
                        erreur = "Un article avec le même titre existe déjà. Veuillez entrer un autre titre."
                        return redirect(
                            url_for('article', identifiant=identifiant,
                                    erreur=erreur))
                    else:
                        # Mettre à jour le titre de l'article
                        identifiant = db.update_article_titre(identifiant,
                                                              nouveau_titre)

                if nouveau_contenu:
                    db.update_article_contenu(identifiant, nouveau_contenu)
    # Si aucune erreur, rediriger vers la page de l'article après la modification
    return redirect(url_for('article', identifiant=identifiant, erreur=erreur))


@app.route('/creation-article', methods=['GET', 'POST'])
@login_required
def creation_article():
    titre = 'Création article'
    date_publication = datetime.date.today()
    # Formater la date au format DD-MM-YYYY
    format_date = date_publication.strftime("%d-%m-%Y")

    if request.method == "GET":
        return render_template("creation_article.html", titre=titre,
                               titre_article="",
                               date_publication=format_date,
                               contenu="", erreur="")
    else:
        erreur = None

        # Récupérer les données du formulaire
        titre_article = request.form.get('titre_article')
        date_publication = request.form.get('date_publication')
        contenu = request.form.get('contenu')

        # Vérifier si l'un des champs est vide
        if not titre_article or not date_publication or not contenu:
            erreur = "Veuillez remplir tous les champs."

        # Vérifier si le titre a au moins 3 caractères
        if len(titre_article) < 3:
            erreur = "Le titre doit avoir au moins 3 caractères."

        # Vérifier si le champ titre dépasse 100 caractères
        if len(titre_article) > 100:
            erreur = "Le titre ne doit pas dépasser 100 caractères."

        # Vérifier si le format de la date est valide
        if not re.match(r'^\d{2}-\d{2}-\d{4}$', date_publication):
            erreur = ("Le format de la date de publication n'est pas valide. "
                      "Utilisez le format DD-MM-YYYY.")

        # Vérifier si le contenu a au moins 15 caractères
        if len(contenu) < 15:
            erreur = "Le contenu doit avoir au moins 15 caractères."

        if erreur != None:
            return render_template("creation_article.html", titre=titre,
                                   titre_article=titre_article,
                                   date_publication=date_publication,
                                   contenu=contenu, erreur=erreur)

        # Insérer l'article dans la base de données
        db = Database()
        id_utilisateur = session.get('id_utilisateur')

        # Vérifier si l'id_article est déjà utilisé
        if db.article_exists(titre_article):
            erreur = ("Un article avec le même titre existe déjà. Veuillez "
                      "en choisir un autre.")
            return render_template("creation_article.html", titre=titre,
                                   titre_article=titre_article,
                                   date_publication=date_publication,
                                   contenu=contenu,
                                   erreur=erreur)

        article = db.create_article(titre_article, date_publication, contenu,
                                    id_utilisateur)

        # Rediriger vers une page de confirmation avec l'ID de l'article créé
        return redirect(
            url_for('confirmation_article', titre_article=titre_article,
                    article=article))


@app.route('/supprimer-article/<identifiant>', methods=['POST'])
@login_required
def supprimer_article(identifiant):
    if identifiant is None:
        return render_template('404.html'), 404

    if request.method == 'POST':
        db = Database.get_db()
        db.delete_article(identifiant)
    return redirect(url_for('articles'))
