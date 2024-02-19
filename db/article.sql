CREATE TABLE ARTICLE (
    id_article INTEGER PRIMARY KEY,
    titre varchar(25) NOT NULL,
    date_publication DATE NOT NULL,
    contenu TEXT NOT NULL,
    id_utilisateur INTEGER NOT NULL,
    CONSTRAINT fk_auteur FOREIGN KEY (id_utilisateur) REFERENCES UTILISATEUR(id_utilisateur)
);