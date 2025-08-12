# CHANGELOG

## 013 - Intégration d'un Modèle de Prédiction par IA

Intégration d'une nouvelle fonctionnalité de prédiction basée sur un modèle
de Machine Learning (Random Forest).

- **Analyse Externe:** Étude du projet `Alphon` pour inspirer l'approche.
- **Création de Modèle:** Développement d'un script (`src/api/analysis/train_model.py`)
  pour entraîner un modèle sur la base d'indicateurs techniques et le sauvegarder.
- **Backend:** Création d'un nouveau service et d'une route d'API (`/api/analysis/<ticker>`)
  pour servir les prédictions (Acheter/Vendre/Conserver) avec un score de confiance.
- **Frontend:** Ajout d'une carte "AI Prediction" dans la vue de détail de l'action
  pour afficher le signal et la confiance du modèle.
- **Dépendances:** Ajout de `scikit-learn` et `joblib` au backend.

## 012 - Passage aux Fichiers CSV Locaux pour les Listes d'Actions

Remplacement de la récupération dynamique des listes d'actions (NASDAQ et CAC40)
par des fichiers CSV locaux. Cette approche améliore considérablement la
fiabilité et la performance de l'application en la rendant indépendante
des services externes. Le code du backend a été simplifié en conséquence.

## 011 - Pluralisation des routes de l'API

Mise à jour des routes de l'API de `/api/stock/` à `/api/stocks/`
pour une meilleure cohérence et le respect des conventions RESTful.
Les tests et le service Angular ont été mis à jour en conséquence.

## 010 - Refactorisation de l'API Backend

Refactorisation majeure du backend Flask. Passage d'une application
monolithique à une architecture modulaire basée sur les fonctionnalités.
La logique métier est maintenant séparée dans des services, et les
routes sont définies dans des Blueprints. Des tests unitaires ont été
ajoutés pour la nouvelle couche de service.

## 009 - Déplacement du dossier API

Déplacement du dossier `api` dans `src/` pour une meilleure
organisation du projet, regroupant tout le code source (frontend et backend)
sous un même répertoire. Les chemins dans la documentation et les scripts
ont été mis à jour.

## 008 - Renommage de l'application en "TradeMind"

Renommage complet de l'application de "stock-app" / "Nasdaq Stock Tracker"
vers "TradeMind" pour mieux refléter les objectifs futurs du projet,
notamment l'intégration d'analyses par IA. Mise à jour de tous les
fichiers de configuration, des titres et du README.

## 007 - Ajout des cotations du CAC40

Ajout de la fonctionnalité d'affichage des actions de l'indice CAC40.
Création d'un nouvel endpoint API et mise à jour de l'interface utilisateur
pour permettre la sélection entre le NASDAQ et le CAC40.

## 006 - Recherche sur les intervalles yfinance

Recherche sur les intervalles de temps disponibles dans `yfinance`.
Échec de la recherche en raison de quotas.
Commit de toutes les modifications.

## 005 - Ajout des tests unitaires pour le backend

Ajout des tests unitaires pour le backend Flask.
Correction des erreurs de sérialisation JSON et des mocks `yfinance`.
Commit de toutes les modifications.

## 004 - Affichage des données historiques sur plusieurs périodes et intervalles

Extension de la fonctionnalité d'affichage des données historiques
pour inclure les périodes de 7 jours, 1 mois et 1 an, avec des intervalles de 1, 5, 15, 30 minutes et 1 heure.

## 003 - Affichage des données historiques avec intervalles 1m, 5m et 15m

Extension de la fonctionnalité d'affichage des données historiques
pour inclure les intervalles de 1, 5 et 15 minutes sur la dernière journée de cotation.

## 002 - Ajout des tests unitaires pour le backend

Ajout des tests unitaires pour le backend Flask.

## 001 - Affichage des données historiques par intervalle de 15 minutes

Ajout de la fonctionnalité d'affichage des données boursières
par intervalle de 15 minutes sur la dernière journée de cotation.
Modification du backend Flask et du frontend Angular.
