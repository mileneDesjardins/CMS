CREATE TABLE UTILISATEUR (
    id_utilisateur INTEGER PRIMARY KEY,
    nom TEXT CHECK(length(nom) <= 30), --ON DOIT FAIRE UNE VALIDATION SI NBRE DE CHAR MAX DANS LE CODE
    prenom TEXT CHECK(length(nom) <= 30),
    courriel TEXT,
    mot_de_passe_hash TEXT NON NULL,
    mot_de_passe_salt TEXT NOT NULL,
    id_photo INTEGER NOT NULL,
    CONSTRAINT fk_photo
        FOREIGN KEY (id_photo)
        REFERENCES PHOTO(id_photo)
);