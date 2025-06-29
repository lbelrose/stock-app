# CHANGELOG

## 001 - Affichage des données historiques par intervalle de 15 minutes

Ajout de la fonctionnalité d'affichage des données boursières
par intervalle de 15 minutes sur la dernière journée de cotation.
Modification du backend Flask et du frontend Angular.

## 002 - Ajout des tests unitaires pour le backend

Ajout des tests unitaires pour le backend Flask.

## 003 - Affichage des données historiques avec intervalles 1m, 5m et 15m

Extension de la fonctionnalité d'affichage des données historiques
pour inclure les intervalles de 1, 5 et 15 minutes sur la dernière journée de cotation.

## 004 - Affichage des données historiques sur plusieurs périodes et intervalles

Extension de la fonctionnalité d'affichage des données historiques
pour inclure les périodes de 7 jours, 1 mois et 1 an, avec des intervalles de 1, 5, 15, 30 minutes et 1 heure.

## 005 - Ajout des tests unitaires pour le backend

Ajout des tests unitaires pour le backend Flask.
Correction des erreurs de sérialisation JSON et des mocks `yfinance`.
Commit de toutes les modifications.

## 006 - Recherche sur les intervalles yfinance

Recherche sur les intervalles de temps disponibles dans `yfinance`.
Échec de la recherche en raison de quotas.
Commit de toutes les modifications.

## 007 - Ajout des cotations du CAC40

Ajout de la fonctionnalité d'affichage des actions de l'indice CAC40.
Création d'un nouvel endpoint API et mise à jour de l'interface utilisateur
pour permettre la sélection entre le NASDAQ et le CAC40.

## 008 - Renommage de l'application en "TradeMind"

Renommage complet de l'application de "stock-app" / "Nasdaq Stock Tracker"
vers "TradeMind" pour mieux refléter les objectifs futurs du projet,
notamment l'intégration d'analyses par IA. Mise à jour de tous les
fichiers de configuration, des titres et du README.
