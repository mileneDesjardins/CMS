CREATE TABLE UTILISATEURS (
    id_utilisateur INTEGER PRIMARY KEY,
    prenom varchar(25) NOT NULL, --ON DOIT FAIRE UNE VALIDATION SI NBRE DE CHAR MAX DANS LE CODE
    nom varchar(25) NOT NULL,
    courriel varchar(100) NOT NULL,
    mdp_hash varchar(128) NOT NULL,
    mdp_salt varchar(32) NOT NULL,
    id_photo INTEGER NOT NULL,
    CONSTRAINT fk_photo
        FOREIGN KEY (id_photo)
        REFERENCES PHOTOS(id_photo)
);