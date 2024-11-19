# Application full stack data DSIA 5102 A

## Description du projet

Le projet consiste en une application web développée avec FastAPI reposant sur une base de données PostgreSQL dont les données 
ont été extraite par Scrapy pour le scraping de données depuis [Pokepedia](https://www.pokepedia.fr/) . 
L'application offre une interface à ses utilisateurs permettant d'interagir avec des données sur les Pokémon. 
L'objectif principal de cette application est de fournir un dashboard où les utilisateurs peuvent :

- Créer un compte et s'authentifier
- Consulter la base de données des pokémons disponible
- Créer leur équipe pokémon et observer, sur la base des valeurs des sensibilités des pokémons, les faiblesses et force de leur équipe
- Avoir accés à une statitique sur la répartition des types de pokémons existants (nombre de pokémon par types)

## Prérequis
Pour exécuter et tester ce projet vous aurez besoin d'avoir accès à :
- Docker
- Docker Compose

[Docker Desktop](https://www.docker.com/products/docker-desktop/) est un logiciel de conterisation disponible gratuitement et indispensable au bon fonctionnement du projet.

## Téléchargement du projet

Pour télécharger le projet vous aurez besoin depuis un terminal de vous placez dans un répertoire où vous souhaitez télécharger le projet puis exécuter 
la commande suivante :
```
git pull  https://github.com/basti2002/DSIA_5102A_Projet.git
```

## Lancement de l'application

Avant de lancer l'application vous aurez besoin avoir démarrer sur votre machine le logiciel
[Docker Desktop](https://www.docker.com/products/docker-desktop/) qui sera utilisé par la suite pour faire fonctionné celui-ci.

Pour utiliser ce projet, suivez les étapes suivantes :

1. **Construction des images Docker** :
   Placez-vous à la racine du projet et exécutez la commande suivante :
   ```docker-compose build```

2. **Démarrage des conteneurs** :
   Une fois réalisé démarrez les conteneurs avec :
   ```docker-compose up -d```

3. **Accès à la page web**
   Puis accédé à la page web à l'adresse local suivante :
   [http://localhost:8000/](http://localhost:8000/)

4. **Arrêt des conteneurs et suppression des volumes** :
   Pour arrêter les conteneurs et supprimer les volumes associés, utilisez :
   ```docker-compose down -v```



## Détails des fonctionnalités présentes de l'application web

### Accéder aux fonctionnalités de l'applciation Web

Vous pourrez accéder à l'application web une fois que les données nécéssaire une fois que la base de données soient remplient.
en effet à chaque démarrage de avec ```docker-compose up -d``` l'application extrait les données du site [Pokepedia](https://www.pokepedia.fr/). Cependant
un écran de chargement est prévu à cet effet pour vous faire patienter et vous redirigera automatiquement sur la page d'acceuil une fois la base de donnée prête. 

### Autoriser l'utilisation des cookies 

Pour autoriser l'utilisation des cookies de votre navigateur et pouvoir accéder aux fonctionnalités d'authentification du site, vous devez lors de votre premièer connexion
autoriser les cookies cliquant sur le bouton "Accepter les cookies" de la fenêtre pop ouverte (en haut à droite de la page).

### Gérer et créer des utilisateurs

Vous pouvez ajouter un utilisateur depuis la page http://localhost:8000/users/manage?

Vous pourrez indiquer :

- le nom d'utilisateur
- le mot de passe associé à ce compte
- Puis cliquer sur "Submit" pour créer le compte

Lors qu'un compte utilisateur est créé celui ci apparaitra dans la "Liste des utilisateurs" juste en dessous de la création d'un compte.

### Observer les pokémon disponible

Vous pourrez observer l'ensemble des pokémon de la base de données disponible sur http://localhost:8000/pokemon/view_db? ou depuis le bouton
"Observer les valeurs de la DB" depuis la page d'acceuil.

### Statitique sur la répartition des types de pokémons existants

Vous pourrez observer un diagramme en barre illusstrant la "Distribution des Types de Pokémon". Ces données
sont filtrées (affichage par défault des 5 types les plus répendus mais modifiable jusqu'à 20 par pas de 5) et afficher
par ordre décroissant (pour montrer les types les plus courant en priorité).

### Connexion à un compte utilisateur

Pour vous connecter à un compte utilisateur vous devrez cliquer sur le bouton "Utilisateur" de la page d'acceuil afin qu'une fenêtre pop up apparaisse en haut
à droite de votre écran. Ainsi vous pourrez renseigner le nom d'utilisateur et le mot de passe associé pour vous connecter.

Si vos identifiants sont correctes et les cookies accéptés, alors vous verrez un message de bienvenu une nouvelle option sur 
la page d'acceuil permettant de voir "Mon équipe Pokémon". 

### Accéder à votre équipe de pokémon et sa statistique de force et faiblesse face aux types existants

Une fois connecté vous pourrez accéder à votre équipe pokémon depuis le bouton "Mon équipe Pokémon" de la page d'acceuil afin d'avoir accés à votre équipe pokémon. 
Par défault votre équipe est vide et vous devrez rajouter manuellement les pokémon pour la constituer (avec un maximum de 6 pokémon).  

Une fois votre équipe de pokémon contitué, vous pourrez voir un diagramme en étoile indiquant les forces (en vert) et les faiblesses (en rouge) de votre équipe pokémon,
ces statiqtiques sont basés sur la somme par types des valeurs des sensibilités de chacun des types de vos pokémon (exemple : la somme des valeurs de sensibilités 
pour le type plante de tout les pokémon de votre équipe). Ainsi vous obtiendrez une vue d'ensemble sur les types pour lesquels
vous serez forts et ceux pour lesquels vous aurez des faiblesses, lors d'un combat pokémon. 


## Difficultés rencontrés

Au cours de ce projet nous avons pu faire face à de nombreux problèmes et avons du trouver les solutions adaptés à ces derniers dont en voici une liste non exaustive :



1) Affichage de toutes les sensibilités :

- Problème : Les sensibilités liées aux types n'étaient pas affichées correctement pour un pokemon 
- Solution : Adaptation de la requête pour récupérer et adaptation du models.py pour établir des relations correctes entre les types du pokémon et ses sensibilités (lié aux types existant).

2) Calcul dynamique des emplacements pour ma modulation de l'équipe pokémon de l'utilisateur :

- Problème : Les emplacements des Pokémon dans l'équipe n'étaient pas recalculés dynamiquement lors de l'ajout ou de la suppression d'un Pokémon. 
- Solution : Implémentation d'une renumérotation des emplacements à chaque modification de l'équipe pour maintenir l'ordre correct.


3) Gestion des erreurs dans les requêtes de base de données :

- Problème : Des erreurs survenaient lors de l'exécution de certaines requêtes, notamment dues à des références incorrectes ou à des objets non trouvés. 
- Solution : Ajout de vérifications et de gestion des cas où les objets attendus ne sont pas trouvés (par exemple, vérification si un Pokémon existe avant de tenter de récupérer ses types et sensibilités).

4) Correction des relations dans les modèles SQLAlchemy :

- Problème : Des erreurs de jointures entre les tables dues à des attributs mal référencés. 
- Solution : Correction des déclarations de clés étrangères et des relations dans les modèles SQLAlchemy pour assurer des jointures correctes et une intégrité référentielle.

5) Intégration et tests des changements dans l'application web :

- Problème : Assurer que les modifications du backend se reflètent correctement dans le frontend, notamment dans les formulaires et l'affichage des données. 
- Solution : Révision du code HTML et des scripts JavaScript pour gérer correctement la nouvelle structure des données (types et sensibilités) et implémentation de tests pour vérifier la fonctionnalité après chaque changement.

6) Gestion de la page de chargement :

- Problème : Afficher une page de chargement pendant que les données sont en cours de récupération. 
- Solution : Implémentation de la logique dans checkDatabase() pour afficher une page html servant d'écran de chargement si le nombre de Pokémon est inférieur à un certain seuil.

## Avertissement

Ce projet réutilise une partie de projet déjà existante (mené par Bastien GUILLOU et Nicolas HAMMEAU réalisé en Data Engineering) 
concernant uniquement les parties concernant Scrapy (extraction des données de poképedia) et PostgreSQL (formation de la base de donnée SQL). 
Cet ancien projet est consultable publiquement sur Github sous le lien si dessous :

https://github.com/WhiteWall13/DataEngineering_Pokepedia


## Auteur

### Bastien Guillou : https://github.com/basti2002
### Ryan KHOU : https://github.com/RyanKHOU