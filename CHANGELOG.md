# CHANGELOG

## 015 - Correction des Imports et Refactorisation du Module Markets

Correction des problèmes d'importation dans le backend Flask et refactorisation du module `markets`.
Suppression de `sys.path.insert` dans `src/api/api.py` au profit de `pyproject.toml`.
Renommage de `src/api/markets/models.py` en `src/api/markets/services.py`.
Mise à jour des imports relatifs et suppression des fichiers de test obsolètes.

## 014 - Refactorisation API, Marchés CSV et Intégration Modèle IA

Refactorisation majeure du backend Flask pour une architecture modulaire, utilisant des fichiers CSV locaux pour les listes d'actions. Intégration d'un modèle de prédiction par IA (Random Forest) avec un nouveau service et une route API dédiée. Le frontend Angular a été mis à jour pour s'adapter à ces changements.

## 013 - Intégration d'un Modèle de Prédiction par IA

Intégration d'une nouvelle fonctionnalité de prédiction basée sur un modèle de Machine Learning (Random Forest).
Développement d'un script pour entraîner un modèle sur indicateurs techniques.
Création d'un service et d'une route API pour servir les prédictions.
Mise à jour du frontend pour afficher le signal et la confiance du modèle.
Ajout des dépendances `scikit-learn` et `joblib`.

## 012 - Passage aux Fichiers CSV Locaux pour les Listes d'Actions

Remplacement de la récupération dynamique des listes d'actions par des fichiers CSV locaux.
Amélioration de la fiabilité et des performances de l'application.
Le code du backend a été simplifié en conséquence.

## 011 - Pluralisation des routes de l'API

Mise à jour des routes de l'API de `/api/stock/` à `/api/stocks/` pour une meilleure cohérence RESTful.
Les tests et le service Angular ont été mis à jour en conséquence.

## 010 - Refactorisation de l'API Backend

Refactorisation majeure du backend Flask vers une architecture modulaire.
La logique métier est séparée dans des services, et les routes sont définies dans des Blueprints.
Des tests unitaires ont été ajoutés pour la nouvelle couche de service.

## 009 - Déplacement du dossier API

Déplacement du dossier `api` dans `src/` pour une meilleure organisation du projet.
Regroupement de tout le code source (frontend et backend) sous un même répertoire.
Les chemins dans la documentation et les scripts ont été mis à jour.

## 008 - Renommage de l'application en "TradeMind"

Renommage complet de l'application pour mieux refléter les objectifs futurs (analyse IA).
Mise à jour de tous les fichiers de configuration, des titres et du README.

## 007 - Ajout des cotations du CAC40

Ajout de la fonctionnalité d'affichage des actions de l'indice CAC40.
Création d'un nouvel endpoint API et mise à jour de l'interface utilisateur.

## 006 - Recherche sur les intervalles yfinance

Recherche sur les intervalles de temps disponibles dans `yfinance`.
Échec de la recherche en raison de quotas.
Commit de toutes les modifications.

## 005 - Ajout des tests unitaires pour le backend

Ajout des tests unitaires pour le backend Flask.
Correction des erreurs de sérialisation JSON et des mocks `yfinance`.

## 004 - Affichage des données historiques sur plusieurs périodes et intervalles

Extension de l'affichage des données historiques pour inclure les périodes de 7 jours, 1 mois et 1 an.
Ajout des intervalles de 1, 5, 15, 30 minutes et 1 heure.

## 003 - Affichage des données historiques avec intervalles 1m, 5m et 15m

Extension de l'affichage des données historiques pour inclure les intervalles de 1, 5 et 15 minutes.
Concerne la dernière journée de cotation.

## 002 - Ajout des tests unitaires pour le backend

Ajout des tests unitaires pour le backend Flask.

## 001 - Affichage des données historiques par intervalle de 15 minutes

Ajout de l'affichage des données boursières par intervalle de 15 minutes.
Concerne la dernière journée de cotation.
Modification du backend Flask et du frontend Angular.