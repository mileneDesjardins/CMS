import sqlite3
import uuid


class Database():

    def __init__(self):
        self.user_connection = None
        self.photo_connection = None
        self.session_connection = None

    def get_user_connection(self):
        if self.user_connection is None:
            self.user_connection = sqlite3.connect('db/utilisateurs.db')
        return self.user_connection

    def get_photo_connection(self):
        if self.photo_connection is None:
            self.photo_connection = sqlite3.connect('db/photos.db')
        return self.photo_connection

    def get_session_connection(self):
        if self.session_connection is None:
            self.session_connection = sqlite3.connect('db/sessions.db')
        return self.session_connection

    def disconnect(self):
        if self.user_connection is not None:
            self.user_connection.close()
        if self.photo_connection is not None:
            self.photo_connection.close()
        if self.session_connection is not None:
            self.session_connection.close()

    def create_user(self, prenom, nom, courriel, mdp_hash, mdp_salt, id_photo):
        connection = self.get_user_connection()
        connection.execute(
            ("insert into utilisateurs(prenom, nom, courriel, mdp_hash, mdp_salt, id_photo)"
             " values(?, ?, ?, ?, ?, ?)"), (prenom, nom, courriel, mdp_hash, mdp_salt, id_photo))
        connection.commit()

    def create_photo(self, file_data):
        id_photo = str(uuid.uuid4())
        connection = self.get_photo_connection()
        connection.execute("insert into photos(id_photo, data) values(?, ?)",
                           [id_photo, sqlite3.Binary(file_data)])
        connection.commit()
        return id_photo

    def get_photo(self, id_photo):
        cursor
        pass

    def save_session(self, id_session, id_utilisateur):
        connection = self.get_session_connection()
        connection.execute(("insert into sessions(id_session, id_utilisateur)"
                            "values(?, ?)"), (id_session, id_utilisateur))
        connection.commit()
        return id_session

    def get_user_login_info(self, courriel):
        cursor = self.get_user_connection().cursor()
        cursor.execute(("select prenom, nom, mdp_hash, mdp_salt, id_photo from utilisateurs where courriel=?"),
                       (courriel,))
        return cursor.fetchone()

    def courriel_existe(self, courriel):
        cursor = self.get_user_connection().cursor()
        cursor.execute("SELECT * FROM utilisateur WHERE courriel LIKE ?", ('%' + courriel + '%',))
        utilisateur_existe = cursor.fetchall()
        if len(utilisateur_existe) == 0:
            return False
        else:
            return True

    def delete_session(self, id_session):
        connection = self.get_user_connection()
        connection.execute(("delete from sessions where id_session=?"),
                           (id_session,))
        connection.commit()

    def get_session(self, id_session):
        cursor = self.get_user_connection().cursor()
        cursor.execute(("select courriel from sessions where id_session=?"),
                       (id_session,))
        data = cursor.fetchone()
        if data is None:
            return None
        else:
            return data[0]
