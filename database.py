import sqlite3
import uuid


class Database():

    def __init__(self):
        self.user_connection = None
        self.photo_connection = None
        self.session_connection = None
        self.article_connection = None

    def disconnect(self):
        if self.user_connection is not None:
            self.user_connection.close()
        if self.photo_connection is not None:
            self.photo_connection.close()
        if self.session_connection is not None:
            self.session_connection.close()
        if self.article_connection is not None:
            self.article_connection.close()

    ### UTILISATEURS
    def get_user_connection(self):
        if self.user_connection is None:
            self.user_connection = sqlite3.connect('db/utilisateurs.db')
        return self.user_connection

    def create_user(self, prenom, nom, username, courriel, mdp_hash, mdp_salt, id_photo):
        connection = self.get_user_connection()
        connection.execute(
            ("insert into utilisateurs(prenom, nom, username, courriel, mdp_hash, mdp_salt, id_photo)"
             " values(?, ?, ?, ?, ?, ?, ?)"), (prenom, nom, username, courriel, mdp_hash, mdp_salt, id_photo))
        connection.commit()

    def get_user_login_info(self, username):
        cursor = self.get_user_connection().cursor()
        cursor.execute((
            "select prenom, nom, mdp_hash, mdp_salt, id_photo from utilisateurs where username=?"),
            (username,))
        return cursor.fetchone()

    def user_exists(self, username):
        cursor = self.get_user_connection().cursor()
        cursor.execute("SELECT * FROM utilisateurs WHERE username LIKE ?", ('%' + username + '%',))
        utilisateur_existe = cursor.fetchall()
        if len(utilisateur_existe) == 0:
            return False
        else:
            return True

    ### ARTICLES
    def get_article_connection(self):
        if self.user_connection is None:
            self.user_connection = sqlite3.connect('db/articles.db')
        return self.user_connection

    def get_articles(self, recherche_input=None):
        cursor = self.get_user_connection().cursor()
        cursor.execute("SELECT * FROM articles WHERE titre LIKE ? OR contenu LIKE ?",
                       ('%' + recherche_input + '%', '%' + recherche_input + '%'))
        return cursor.fetchall()

    def create_article(self, titre_article, date_publication, contenu, id_utilisateur):
        connection = self.get_article_connection()
        id_article = str(uuid.uuid4())
        connection.execute(
            "INSERT INTO articles (id_article, titre_article, date_publication, contenu, id_utilisateur) VALUES (?, ?, ?, ?, ?)",
            (id_article, titre_article, date_publication, contenu, id_utilisateur)
            )
        connection.commit()
        return id_article

    ### PHOTOS
    def get_photo_connection(self):
        if self.photo_connection is None:
            self.photo_connection = sqlite3.connect('db/photos.db')
        return self.photo_connection

    def create_photo(self, photo_data):
        id_photo = str(uuid.uuid4())
        connection = self.get_photo_connection()
        connection.execute("insert into photos(id_photo, data) values(?, ?)",
                           [id_photo, sqlite3.Binary(photo_data)])
        connection.commit()
        return id_photo

    def get_photo(self, id_photo):
        cursor = self.get_photo_connection().cursor()
        cursor.execute("SELECT data FROM photos WHERE id_photo=?", (id_photo,))
        photo_data = cursor.fetchone()
        if photo_data:
            return photo_data[0]
        else:
            return None

    ### SESSIONS
    def get_session_connection(self):
        if self.session_connection is None:
            self.session_connection = sqlite3.connect('db/sessions.db')
        return self.session_connection

    def get_session(self, id_session):
        cursor = self.get_session_connection().cursor()
        cursor.execute(("select utilisateur from sessions where id_session=?"),
                       (id_session,))
        data = cursor.fetchone()
        if data is None:
            return None
        else:
            return data[0]

    def save_session(self, id_session, username):
        connection = self.get_session_connection()
        connection.execute(("insert into sessions(id_session, utilisateur)"
                            "values(?, ?)"), (id_session, username))
        connection.commit()
        return id_session

    def delete_session(self, id_session):
        connection = self.get_session_connection()
        connection.execute(("delete from sessions where id_session=?"),
                           (id_session,))
        connection.commit()
