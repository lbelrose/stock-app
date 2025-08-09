# CHANGELOG

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