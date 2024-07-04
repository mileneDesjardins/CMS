<p>Ce projet consiste en la conception d'un CMS (Content Management System) simplifié pour la gestion de contenu de sites web. 
  Le CMS permet aux utilisateurs ayant un compte de créer, modifier et supprimer des articles. Il est aussi possible pour eux de créer et désactiver un utilisateur ainsi que modifier les informations de celui-ci</p>

<h2>Insallation</h2>

1. Assurez-vous d'avoir installer Python sur votre système: https://www.python.org/downloads/

2. Installer Flask et pycodestyle à l'aide de pip, le gestionnaire de paquets de Python:

```bash

pip install Flask pycodestyle

```

3. Installer toutes les librairies incluses dans le fichier requirements.txt:
   
```bash

pip install -r requirements.txt

```

4. Exécuter l'application Flask

```bash

flask --debug run

```

5. Entrer l'url suivant dans un fureteur tel que Chrome, Firefox ou Edge:
http://127.0.0.1:5000


<h2>Base de données</h2>
Il y a 3 bases de données existantes:

  - articles.db
  - photos.db
  - utilisateurs.db

<h2>Routes</h2>
Le CMS doit supporter plusieurs routes pour différentes fonctionnalités. Voici les principales routes exigées :

GET /: 
  - Page d'accueil affichant les 5 dernières publications et un champ de recherche.
    ![image](https://github.com/mileneDesjardins/CMS/assets/106025922/1a60e2dc-1634-454e-aee1-9b15f7954200)

GET /article/&lt;identifiant&gt; : 
  - Page d'un article spécifique.
    ![image](https://github.com/mileneDesjardins/CMS/assets/106025922/998cdfba-cd05-4b8a-a25a-d276c5022b05)
  - Page d'un article pouvant être modifiée, après authentification.
    ![image](https://github.com/mileneDesjardins/CMS/assets/106025922/d6214371-2e2e-4e9b-ab44-caf258550ef7)

GET /admin : 
  - Point d'entrée pour l'administration du site, elle redirige à une page qui présente la liste de tous les articles, accessible après authentification.
    ![image](https://github.com/mileneDesjardins/CMS/assets/106025922/c8519f1a-2fdb-4ab4-974b-f8a8c3e6450a)

GET /admin-nouveau : 
  - Page de création d'un nouvel article, accessible après authentification.
    ![image](https://github.com/mileneDesjardins/CMS/assets/106025922/7f08aaae-a828-439d-beb3-6c6ce26837ef)

GET /utilisateurs : 
  - Page d'administration des utilisateurs, accessible après authentification.
    ![image](https://github.com/mileneDesjardins/CMS/assets/106025922/90da1079-e2db-4a52-b3e9-9a3db8ea8a90)

GET /modifier-utilisateur/id :
  - Page pour modifier un utilisateur, accessible apres authentification.
    ![image](https://github.com/mileneDesjardins/CMS/assets/106025922/55a5147d-22fe-412e-9fdd-6045a3d0c6b8)
    

<h2>Technologies Utilisées</h2>

<h3>Front-end</h3>

  - HTML 5
  - CSS 3
  - JavaScript
  - Bootstrap

<h3>Back-end</h3>

  - Python
  - Flask
  - Jinja


