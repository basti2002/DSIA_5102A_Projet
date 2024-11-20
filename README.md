# Application full stack data DSIA 5102 A

## Description du projet

Le choix de notre sujet se porte sur l'univers du jeu vidéo Pokémon, où chaque créature possédent des types qui déterminent ses forces et faiblesses. 
Notre application web se concentre sur l'analyse de ces types pour aider les joueurs à comprendre et à optimiser leurs stratégies de combat. 
En fournissant des outils pour explorer les interactions entre les types, l'application vise à améliorer la compréhension des combats et à 
offrir une vue complète des avantages et désavantages de chaque type dans une équipe Pokémon afin de le rendre plus accessible aux novices.


Le projet consiste en une application web développée avec FastAPI reposant sur une base de données PostgreSQL dont les données 
ont été extraites par Scrapy pour le scraping de données depuis [Pokepedia](https://www.pokepedia.fr/) . 
L'application offre une interface à ses utilisateurs permettant d'interagir avec des données sur les Pokémon. 
L'objectif principal de cette application est de fournir un dashboard où les utilisateurs peuvent :

- Créer un compte et s'authentifier
- Consulter la base de données des Pokémon disponibles
- Créer leur équipe Pokémon et observer, sur la base des valeurs et des sensibilités des Pokémon, les faiblesses et forces de leur équipe
- Avoir accès à une statistique sur la répartition des types de Pokémon existants (nombre de Pokémon par type)


## Prérequis
Pour exécuter et tester ce projet, vous aurez besoin d'avoir accès à :
- Docker
- Docker Compose

[Docker Desktop](https://www.docker.com/products/docker-desktop/) est un logiciel de conterisation disponible gratuitement et indispensable au bon fonctionnement du projet.

## Téléchargement du projet

Pour télécharger le projet, vous aurez besoin depuis un terminal de vous placer dans un répertoire où vous souhaitez télécharger le projet, puis exécuter
la commande suivante :
```
git pull  https://github.com/basti2002/DSIA_5102A_Projet.git
```

## Lancement de l'application

Avant de lancer l'application, vous aurez besoin avoir démarré sur votre machine le logiciel
[Docker Desktop](https://www.docker.com/products/docker-desktop/) qui sera utilisé par la suite pour faire fonctionné celui-ci.

Pour utiliser ce projet, suivez les étapes suivantes :

1. **Construction des images Docker** :
   Placez-vous à la racine du projet et exécutez la commande suivante :
   ```docker-compose build```

2. **Démarrage des conteneurs** :
   Une fois réalisé démarrez les conteneurs avec :
   ```docker-compose up -d```

3. **Accès à la page web**
   Puis accéder à la page web à l'adresse local suivante :
   [http://localhost:8000/](http://localhost:8000/)

4. **Arrêt des conteneurs et suppression des volumes** :
   Pour arrêter les conteneurs et supprimer les volumes associés, utilisez :
   ```docker-compose down -v```



## Détails des fonctionnalités présentes de l'application web

### Accéder aux fonctionnalités de l'applciation Web

Vous pourrez accéder à l'application web une fois que les données nécessaires seront remplies.
En effet, à chaque démarrage avec ```docker-compose up -d```, l'application extrait les données du site [Pokepedia](https://www.pokepedia.fr/). Cependant
un écran de chargement est prévu à cet effet pour vous faire patienter et vous redirigera automatiquement sur la page d'accueil une fois la base de données prête.

### Autoriser l'utilisation des cookies 

Pour autoriser l'utilisation des cookies de votre navigateur et pouvoir accéder aux fonctionnalités d'authentification du site, vous devez, 
lors de votre première connexion
autoriser les cookies en cliquant sur le bouton "Accepter les cookies" de la fenêtre pop ouverte (en haut à droite de la page).

### Gérer et créer des utilisateurs

Vous pouvez ajouter un utilisateur depuis la page http://localhost:8000/users/manage?

Vous pourrez indiquer :

- le nom d'utilisateur
- le mot de passe associé à ce compte
- Puis cliquer sur "Créer" pour créer le compte

Lorsqu'un compte utilisateur est créé, celui-ci apparaitra dans la "Liste des utilisateurs" juste en dessous de la création d'un compte.

### Observer les Pokémon disponibles

Vous pourrez observer l'ensemble des pokémon de la base de données disponible sur http://localhost:8000/pokemon/view_db? ou depuis le bouton
"Observer les Pokémon disponibles" depuis la page d'acceuil.

### Statitique sur la répartition des types de pokémons existants

Vous pourrez observer un diagramme en barre illustrant la "Distribution des Types de Pokémon". Ces données
sont filtrées (affichage par défaut des 5 types les plus répendus mais modifiable jusqu'à 20 par pas de 5) et affichées
par ordre décroissant (pour montrer les types les plus courants en priorité).

### Connexion à un compte utilisateur

Pour vous connecter à un compte utilisateur, vous devrez cliquer sur le bouton "Utilisateur" de la page d'accueil afin qu'une fenêtre pop-up apparaisse en haut
à droite de votre écran. Ainsi, vous pourrez renseigner le nom d'utilisateur et le mot de passe associé pour vous connecter.

Si vos identifiants sont corrects et les cookies acceptés, alors vous verrez un message de bienvenue, une nouvelle option sur
la page d'accueil permettant de voir "Mon équipe Pokémon". 

### Accéder à votre équipe de Pokémon et à ses statistiques de force et de faiblesse face aux types existants

Une fois connecté, vous pourrez accéder à votre équipe Pokémon depuis le bouton "Mon équipe Pokémon" de la page d'accueil afin d'avoir accès à votre équipe Pokémon.
Par défaut, votre équipe est vide et vous devrez rajouter manuellement les Pokémon pour la constituer (avec un maximum de 6 Pokémon).

Une fois votre équipe de Pokémon constituée, vous pourrez voir un diagramme en étoile indiquant les forces (en vert) et les faiblesses (en rouge) 
de votre équipe Pokémon,
ces statistiques sont basées sur la somme par types des valeurs des sensibilités de chacun des types de vos Pokémon (exemple : la somme des valeurs de sensibilités )
pour le type plante de tous les Pokémon de votre équipe). Ainsi, vous obtiendrez une vue d'ensemble sur les types pour lesquels
vous serez forts et ceux pour lesquels vous aurez des faiblesses, lors d'un combat Pokémon.


## Difficultés rencontrées

Au cours de ce projet, nous avons pu faire face à de nombreux problèmes et avons dû trouver les solutions adaptées à ces derniers, dont en voici une liste de 
diverses problèmes rencontrés pendant son développement :



1) Affichage de toutes les sensibilités :

- Problème : Les sensibilités liées aux types n'étaient pas affichées correctement pour un Pokémon. 
- Solution : Adaptation du models.py pour les relations entre les types du pokémon et ses sensibilités (lié aux types existant) puis de la requête de FastAPI pour 
récupérer correctement ces données.

2) Calcul dynamique des emplacements de l'équipe pokémon de l'utilisateur :

- Problème : Les emplacements des Pokémon dans l'équipe n'étaient pas recalculés correctement et dynamiquement lors de l'ajout ou de la suppression d'un Pokémon. 
- Solution : Implémentation d'une renumérotation des emplacements à chaque modification de l'équipe pour maintenir l'ordre correct, meilleure gestion des donénes entre le back et le front end.


3) Gestion des erreurs dans les requêtes de base de données :

- Problème : Des erreurs survenaient lors de l'exécution de certaines requêtes, dues à des références incorrectes ou à des objets non trouvés. 
- Solution : Ajout de vérifications et de gestion des cas où les objets attendus ne sont pas trouvés.

4) Correction des relations dans les modèles SQLAlchemy :

- Problème : Des erreurs de jointures entre les tables dues à des attributs mal référencés. 
- Solution : Correction des déclarations de clés étrangères et des relations dans les modèles SQLAlchemy pour assurer des jointures correctes.

5) Intégration et tests des changements dans l'application web :

- Problème : Assurer que les modifications du backend se reflètent correctement dans le frontend, notamment dans les formulaires et l'affichage des données. 
- Solution : Révision du code HTML et des scripts JavaScript pour gérer correctement la nouvelle structure des données (types et sensibilités) et implémentation de tests pour vérifier la fonctionnalité après chaque changement.

6) Gestion de la page de chargement :

- Problème : Afficher une page de chargement pendant que les données sont en cours de récupération. 
- Solution : Implémentation de la logique dans checkDatabase() pour afficher une page html servant d'écran de chargement si le nombre de Pokémon est inférieur à un certain seuil.

7) Affichage conditionnel de la page :

- Problème : Il fallait s'assurer que la page s'affiche de manière anonyme si aucun utilisateur n'était connecté, tout en permettant une expérience personnalisée pour les utilisateurs authentifiés. 
- Solution : Utilisation de Jinja2 dans home.html pour conditionner l'affichage des éléments de l'interface utilisateur en fonction de l'état de connexion de 
l'utilisateur. Si le token JWT est valide et correspond à un utilisateur, les détails de l'utilisateur sont affichés ; sinon, l'interface reste en mode non connecté.

8) Suppression des cookies à chaque démarrage de l'application :

- Problème : Nécessité d'éviter une connexion automatique avec des cookies obsolètes (issu de précédente connexion mais toujours enregistré par le navigateur)
qui pourraient référencer un compte supprimé ou invalide.
- Solution : Implémentation d'un middleware dans main.py qui vérifie à chaque requête l'existence et la validité du token stocké dans les cookies. Si le token est invalide ou si l'utilisateur ne correspond pas, le cookie est supprimé pour forcer une nouvelle authentification.

9) Gestion complexe des cookies :

- Problème : Les cookies doivent être gérés de manière sécurisée pour éviter les accès non autorisés, tout en étant accessible côté client pour les opérations nécessaires comme la déconnexion. 
- Solution : Régler l'attribut HttpOnly sur False pour permettre au script côté client (front end) de lire le cookie et de gérer la déconnexion. 
De plus le paramètre cookie secure est réglé sur False pour permettre des tests en développement sans HTTPS, même si celui ci devrait normalement être réglé sur True pour renforcer la sécurité.
Cependant pour les attendus ce de projet un niveau de sécurité élevé n'était pas requis, nous avons fait un compromis entre efficacité des fonctionnalités
de l'application et la sécurité globale (si l'application était déployé à plus grande échelle).

## Avertissement réutilisation de partie de projet

Ce projet réutilise une partie du projet déjà existante (mené par Bastien GUILLOU et Nicolas HAMMEAU, réalisé en Data Engineering l'année scolaire dernière)
Concernant uniquement les parties concernant Scrapy (extraction des données de poképedia) et PostgreSQL (formation de la base de données SQL).

> Cet ancien projet est consultable publiquement sur Github sous le lien ci-dessous : https://github.com/WhiteWall13/DataEngineering_Pokepedia


## Auteur

### Bastien Guillou : https://github.com/basti2002
### Ryan KHOU : https://github.com/RyanKHOU