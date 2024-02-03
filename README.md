# Projet TALN2 - Extraction de relations

Ce projet à pour but d'extraire des relations entre les entités d'une phrase choisie, en utilisant les données de [JeuxDeMots](http://www.jeuxdemots.org/).

## Prérequis

- Python 3.8  
- librairies sqlite3, matplotlib, networkx  
`pip install sqlite3`, `pip install matplotlib`, `pip install networkx`  
- les fichiers `txt/mots-composés.txt` et `txt/regles.txt` doivent être présents dans le dossier `txt/`

## Utilisation
Lancer le programme avec la commande suivante:
`python main.py`, puis entrez la phrase de votre choix.

Vous pouvez ajouter ou retirer certaines options en les modifiant dans le fichier `main.py` à la ligne 10 :
```Python
VERBOSE = 0            # Activer tous les affichages
VISUALISE_GRAPH = 1    # Visualiser le graphe
DELETE_DATABASE = 0    # Effacer entièrement la base
```