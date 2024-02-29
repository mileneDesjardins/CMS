CREATE TABLE ARTICLES (
    id_article INTEGER PRIMARY KEY,
    titre_article varchar(25) NOT NULL,
    date_publication DATE NOT NULL,
    contenu TEXT NOT NULL,
    id_utilisateur INTEGER NOT NULL,
    CONSTRAINT fk_auteur FOREIGN KEY (id_utilisateur) REFERENCES UTILISATEURS(id_utilisateur)
);