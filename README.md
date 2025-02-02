# Bienvenue sur EcoLogement

Le serveur principale se situe sur le fichier python  ```serveurNeo1.py```.  Pour le lancer il faut donc lancer sur la commande suivante dans un termale ```python3 serveurNeo1.py ``` .

Ceci lancera le serveur (sur le port 8888) et une page web apparaîtra. On peut également écrire sur dans la barre d'adresse d'un navigateur le lien suivant pour accéder à la page d'accueil : ```http://localhost:8888/```

Dans le projet, il y a deux fichiers (des scripts bash) qui permettent de remplir les factures ```remplir_facture.sh``` ou les mesures ```remplir_mesure.sh```

![Diagramme de l'architecture](Image/EcranAccueil.png)


## Page d'accueil

La page d'accueil se compose d'une image de fond avec 5 rectangles sur lequel on peut cliquer :
- Une page ```facture``` qui permet de consulter la consommation de la maison
- Une page ```météo``` qui permet d'avoir les prévisions sur 2 échelles de temps (2 jours - 5 jours)
- Une page ```capteur``` qui permet de visualiser en temps réel les données de mesures de la base de données
- Une page ```actionneur``` qui permet de manipuler les actionneurs de la maison
- Une page ```configuration``` qui permet d'ajourer / supprimer les factures et les mesures de la base de données

Chaque page du site dispose d'un bouton ```Home``` permettant de revenir à la page d'accueil.

## Facture 

Cette page permet de voir en temps réelle la consommation liées aux factures de la base de données. On peut choisir différents échelle de temps (3 mois - 6 mois - 12 mois). On peut voir alors 3 courbes (eau -électricité et gaz). 

## Météo

Cette page permet de visualiser les prévisions météorologiques sur paris sur 2 échelles de temps (2 jours ou 5 jours). Pour cela, on utilise une API vers le site ```openweathermap.org``` pour avoir des données réelles

## Capteur

Cette page permet de suivre en temps réelle les données des mesures issues de la base de données. Pour ```id``` de chaque capteur, on affichera une jauge distinctes. L'utilisateur peut choisir 2 vues au choix :
- Une vue avec des jauges qui permet de connaitre la dernières données de la base de données 
- Une vue sous forme de graphique (courbes) pour suivre l'évolution de la valeur au cours du temps

On affiche uniquement si il existe des mesures associés à un capteur

## Actionneur 

Cet page permet de manipuler les actionneurs (dans notre cas il s'agira uniquement de la LED de l'ESP8266), la page dispose d'un bouton à actionneur pour contôler la LED. Il y a également une animation rendant l'expérience utilisateur dynamique est agréable.
Il faut éventuellement cliquer une première fois pour synchroniser la LED et le site.

## Configuration

Cette page permet de voir les factures et les mesures de la base de données. L'utilité principale de cette page et de pouvoir intéragir avec la base de données de manière dynamique et en temps réel. La suppression ou l'ajout de facture/mesure se verra instantannément sur les pages correspondantes ``` facture / capteur ```
