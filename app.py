import os
from dotenv import load_dotenv
from flask import Flask, render_template, g, session, \
    Response, redirect, url_for

from authorization_decorator import login_required
from database import Database

load_dotenv()
app = Flask(__name__, static_url_path='', static_folder='static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

import articles
import utilisateurs
import recherche
import confirmation


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.disconnect()


@app.errorhandler(404)
def not_found(e):
    titre = 'Page 404'
    return render_template("404.html", titre=titre), 404


@app.route('/', methods=['GET'])
def accueil():
    titre = 'Accueil'
    if "id" in session:
        prenom = session.get('prenom')
        nom = session.get('nom')
    else:
        prenom = None
        nom = None

    db = Database.get_db()
    articles = db.get_cinq_dernier_articles()

    # Liste des ID utilisateur des cinq derniers articles
    id_utilisateurs = [article[4] for article in articles]

    # Liste des informations des utilisateurs correspondant à ces ID
    utilisateurs = [db.get_user_by_id(id_utilisateur) for id_utilisateur in
                    id_utilisateurs]

    photos = [db.get_photo(utilisateur[7]) for utilisateur in utilisateurs]

    return render_template('index.html', titre=titre, prenom=prenom,
                           photos=photos, nom=nom, articles=articles,
                           utilisateurs=utilisateurs)


@app.route('/photo/<id_photo>')
def photo(id_photo):
    photo_data = Database.get_db().get_photo(id_photo)
    if photo_data:
        return Response(photo_data, mimetype='application/octet-stream')


@app.route('/admin', methods=['GET'])
@login_required
def admin():
    return redirect(url_for('articles'))


@app.route('/admin-nouveau', methods=['GET', 'POST'])
@login_required
def admin_nouveau():
    return redirect(url_for('creation_article'))


if __name__ == '__main__':
    app.run()
