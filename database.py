import sqlite3


class Database():

    def __init__(self):
        self.connection = None

    def get_connection(self):
        if self.connection is None:
            self.connection = sqlite3.connect('db/utilisateur.db')
        return self.connection

    def deconnection(self):
        if self.connection is not None:
            self.connection.close()

    def creer_utilisateur(self, prenom, nom, courriel, mot_de_passe_hash, mot_de_passe_salt, photo):
        connection = self.get_connection()
        connection.execute(
            ("insert into utilisateur(prenom, nom, courriel, mot_de_passe_hash, mot_de_passe_salt, photo)"
             " values(?, ?, ?, ?, ?, ?)"), (prenom, nom, courriel, mot_de_passe_hash, mot_de_passe_salt, photo))
        connection.commit()

    def courriel_existe(self, courriel):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM utilisateur WHERE courriel = LIKE", ('%' + courriel + '%',))
        utilisateur_existe = cursor.fetchall()
        if len(utilisateur_existe) == 0:
            return False
        else:
            return True

    def get_user_login_info(self, username):
        cursor = self.get_connection().cursor()
        cursor.execute(("select salt, hash from users where utilisateur=?"),
                       (username,))
        user = cursor.fetchone()
        if user is None:
            return None
        else:
            return user[0], user[1]

    def save_session(self, id_session, username):
        connection = self.get_connection()
        connection.execute(("insert into sessions(id_session, utilisateur) "
                            "values(?, ?)"), (id_session, username))
        connection.commit()

    def delete_session(self, id_session):
        connection = self.get_connection()
        connection.execute(("delete from sessions where id_session=?"),
                           (id_session,))
        connection.commit()

    def get_session(self, id_session):
        cursor = self.get_connection().cursor()
        cursor.execute(("select utilisateur from sessions where id_session=?"),
                       (id_session,))
        data = cursor.fetchone()
        if data is None:
            return None
        else:
            return data[0]
