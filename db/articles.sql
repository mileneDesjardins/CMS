CREATE TABLE ARTICLES (
    id_article VARCHAR(100) PRIMARY KEY,
    titre_article varchar(100) NOT NULL,
    date_publication DATE NOT NULL,
    contenu TEXT NOT NULL,
    id_utilisateur INTEGER NOT NULL,
    CONSTRAINT fk_auteur FOREIGN KEY (id_utilisateur) REFERENCES UTILISATEURS(id_utilisateur)
);