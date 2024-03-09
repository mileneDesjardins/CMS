from flask import render_template, request
from app import app


@app.route('/confirmation_utilisateur', methods=['GET'])
def confirmation():
    titre = 'Création réussie'
    return render_template('confirmation_utilisateur.html', titre=titre)


@app.route('/confirmation_article', methods=['GET'])
def confirmation_article():
    titre = "Création réussie"
    titre_article = request.args.get('titre_article')
    return render_template('confirmation_article.html', titre=titre,
                           titre_article=titre_article)
