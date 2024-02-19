CREATE TABLE UTILISATEUR (
    id_utilisateur INTEGER PRIMARY KEY,
    nom varchar(25) NOT NULL, --ON DOIT FAIRE UNE VALIDATION SI NBRE DE CHAR MAX DANS LE CODE
    prenom varchar(25) NOT NULL,
    courriel varchar(100) NOT NULL,
    mot_de_passe_hash varchar(128) NOT NULL,
    mot_de_passe_salt varchar(32) NOT NULL,
    id_photo INTEGER NOT NULL,
    CONSTRAINT fk_photo
        FOREIGN KEY (id_photo)
        REFERENCES PHOTO(id_photo)
);