from flask import request, app, redirect, url_for, render_template
from app import app

from database import Database


@app.route('/recherche', methods=['POST'])
def recherche():
    recherche_input = request.form.get("recherche_input")
    if not recherche_input:
        # Si aucun terme de recherche n'est saisi, rediriger vers la page de
        # résultats sans terme de recherche
        return redirect(url_for('resultats')), 302
    else:
        # Effectuer la recherche avec le terme saisi par l'utilisateur
        return redirect(url_for('resultats', query=recherche_input)), 302


@app.route('/resultats/<query>', methods=['GET'])
@app.route('/resultats/', defaults={'query': None}, methods=['GET'])
def resultats(query):
    titre="Résultats"
    if query:
        # Effectuer la recherche en fonction du terme de recherche (query) et
        # récupérer les articles correspondants
        db = Database.get_db()
        articles = db.get_articles(query)
    else:
        # Si aucun terme de recherche n'est spécifié, récupérer tous les
        # articles
        db = Database.get_db()
        articles = db.get_articles()

    return render_template('resultats.html', query=query, articles=articles,
                           titre=titre)
