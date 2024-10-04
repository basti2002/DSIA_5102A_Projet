Rendu attendu:
Lien vers un Repository Github : https://docs.google.com/spreadsheets/d/15QkiTOW7Z7UWIXDLuv7nTV5C9My5bhaous86IstMPO4/edit?gid=0#gid=0
Un readme expliquant le sujet choisi, les difficultés rencontrées ainsi qu’une petite explication sur le lancement de l’application
 
Critères d’évaluation:
 
Le projet doit se lancer intégralement avec docker compose
Le projet doit contenir au moins deux services.
Une API écrite en python avec FastAPI
Une base de données Postgresql
La base de données contiendra une table User
Un système d’authentification devra être mis en place
Soit un simple système comme vu en cours
Récupération d’un JWT à l’aide d’un username / password
Soit avec le système d’authentification Keycloak
Au moins un endpoint d’API sécurisé à l’aide d’une authentification JWT
Une suite de tests unitaire devront accompagner le code de l’API
Gestion des erreurs HTTP avec try / except
Pas d’erreur 500
401 et 403 et 404
https://fr.wikipedia.org/wiki/Liste_des_codes_HTTP
 
 
Conseils:
Soyez inventifs, nous avons vu en cours un exemple d’API CRUD. Les endpoints que vous implémenterez pour le projet peuvent être plus élaborés
Ajoutez des filtres, des calculs…
Vous pouvez partir de données existantes et les intégrer dans la base de données au lancement du serveur avec un script python
Pour les étudiants qui ont effectué un projet Dash en E4, une bonne idée de projet serait de conteneuriser le projet. Les données seraient lu depuis la base de données plutôt que dans un fichier
 
 
 
Exemples de projets:
Création de blog
Des articles, des auteurs, des commentaires…
Exemple d’endpoint: récupérer tous les articles d’un certain auteur…
Catalogue de musique
Artistes, morceaux…
Vous pouvez trouver de nombreuses idées de projet sur Kaggle
