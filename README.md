<h1>TP1 - INF5190</h1>
<p>Ce projet consiste en la conception d'un CMS (Content Management System) simplifié pour la gestion de contenu de sites web. 
  Le CMS permet aux utilisateurs ayant un compte de créer, modifier et supprimer des articles. Il est aussi possible pour eux de créer et désactiver un utilisateur ainsi que modifier les informations de celui-ci</p>

<h2>Insallation</h2>

1. Assurez-vous d'avoir installer Python sur votre système.

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

<h2>Base de données</h2>
Il y a 3 bases de données existantes:

  - articles.db
  - photos.db
  - utilisateurs.db

<h2>Routes</h2>
Le CMS doit supporter plusieurs routes pour différentes fonctionnalités. Voici les principales routes exigées :

GET /: 
  - Page d'accueil affichant les 5 dernières publications et un champ de recherche.

GET /article/&lt;identifiant&gt; : 
  - Page d'un article spécifique.

GET /admin : 
  - Point d'entrée pour l'administration du site, elle redirige à une page qui présente la liste de tous les articles, accessible après authentification.

GET /admin-nouveau : 
  - Page de création d'un nouvel article, accessible après authentification.

GET /utilisateurs : 
  - Page d'administration des utilisateurs, accessible après authentification.

<h2>Technologies Utilisées</h2>

<h3>Front-end</h3>

  - HTML 5
  - CSS 3
  - JavaScript (si nécessaire)
  - JQuery (si nécessaire)
  - Bootstrap (si nécessaire)

<h3>Back-end</h3>

  - Python (standard)
  - Flask (doit être installé)


