# CHANGELOG

## 026 - Scripts d'Entraînement et de Prédiction Génériques

- Introduction de scripts génériques pour l'entraînement et la prédiction des modèles IA :
    - Création de `model_configs.json` pour centraliser les hyperparamètres des différents types de modèles.
    - Création de `generic_train_all_models.py` pour entraîner tous les modèles spécifiés dans `optimized_thresholds.json` en utilisant les configurations de `model_configs.json` et la nouvelle architecture modulaire.
    - Création de `predict_next_day.py` (anciennement inexistant) pour effectuer des prédictions en utilisant la nouvelle architecture modulaire et les seuils optimisés.
- Mise à jour de `optimized_thresholds.json` pour inclure le `model_class_name` pour chaque ticker, assurant la compatibilité avec la nouvelle architecture.

## 025 - Amélioration de l'Évaluation du Modèle avec Validation Croisée Temporelle

- Implémentation d'une évaluation plus robuste des modèles dans `train_model.py` en utilisant la validation croisée temporelle (`TimeSeriesSplit`).
- Calcul et affichage des métriques de performance (précision, rappel, F1-score, exactitude) pour chaque split de validation.
- Calcul et affichage des moyennes de ces métriques sur l'ensemble des splits pour une évaluation plus fiable de la généralisation du modèle.

## 024 - Modularisation de l'Architecture des Modèles IA

- Introduction d'une architecture modulaire pour les modèles de prédiction :
    - Création d'une classe abstraite `BaseModel` (`src/api/analysis/models/base_model.py`) pour définir une interface commune (entraînement, prédiction, sauvegarde, chargement).
    - Implémentation d'une classe de modèle concrète `RandomForestModel` (`src/api/analysis/models/random_forest_model.py`) héritant de `BaseModel`.
    - Création d'un `ModelFactory` (`src/api/analysis/models/model_factory.py`) pour l'instanciation dynamique des modèles.
- Adaptation des scripts `train_model.py` et `backtest.py` pour utiliser cette nouvelle architecture modulaire, permettant une gestion et une extension plus faciles des différents types de modèles.

## 023 - Amélioration des Métriques de Backtesting

- Ajout de nouvelles métriques de performance au script de backtesting (`src/api/analysis/backtest.py`) :
    - **Précision Directionnelle (Directional Accuracy)** : Pour évaluer la capacité du modèle à prédire correctement la direction du marché les jours où un signal d'achat est généré.
    - **Drawdown Maximal (Max Drawdown)** : Pour mesurer le risque de la stratégie en identifiant la plus grande perte de capital.
    - **Ratio de Sharpe (Sharpe Ratio)** : Pour évaluer le rendement ajusté au risque de la stratégie (avec un taux sans risque de 0 pour l'instant).
- Mise à jour du rapport de backtesting et des résultats sauvegardés pour inclure ces nouvelles métriques.

## 022 - Re-exécution des Backtests avec Seuils Optimisés

- Re-exécution des backtests pour tous les tickers sur la période du 1er semestre 2025 (01/01/2025 au 30/06/2025).
- Utilisation des seuils d'achat optimisés et des modèles spécifiques à chaque action, chargés depuis `optimized_thresholds.json`.
- Les résultats des backtests ont été sauvegardés dans le répertoire `src/api/analysis/backtest_results`.
- Correction de l'erreur d'importation relative dans `src/api/analysis/backtest.py` en changeant `from .features import generate_technical_features` en `from features import generate_technical_features`.
- Création et suppression d'un script temporaire `run_all_backtests.py` pour orchestrer l'exécution des backtests.

## 021 - Refactorisation Frontend : Migration des Templates/Styles et Signals

- Migration des templates et styles inline vers des fichiers dédiés pour `StockCardComponent` et `StockSearchComponent`.
- Conversion des propriétés réactives en `signals` pour `StockCardComponent` (`isInWatchlist`) et `StockSearchComponent` (`searchQuery`, `searchResults`, `showResults`).
- Application de `ChangeDetectionStrategy.OnPush` pour `StockSearchComponent`.

## 020 - Intégration des Seuils Optimisés de Prédiction

- Intégration des seuils d'achat optimisés par ticker dans le script de prédiction.
- Le script `predict_next_day.py` utilise désormais les seuils et modèles spécifiques à chaque action, chargés depuis `optimized_thresholds.json`.
- Correction d'une `NameError` dans `services.py` en remplaçant `generate_prediction_features` par `generate_technical_features`.

## 019 - Refactorisation Frontend et Mise à Jour Angular 21

- Refactorisation des composants Dashboard et Header.
- Migration des templates et styles inline vers des fichiers dédiés.
- Implémentation de la gestion d'état avec les signaux Angular pour le Dashboard.
- Application de `ChangeDetectionStrategy.OnPush` pour le Dashboard.
- Mise à jour d'Angular vers la version 21.

## 018 - Mise à Jour des Dépendances et Script de Backtesting

- Mise à jour des dépendances Python et Angular.
- Modification du script de backtesting pour utiliser `argparse`.
- Réactivation de la persistance des préférences de marché sur le tableau de bord.
- Suppression de l'ancien modèle `random_forest_model.joblib`.

## 017 - Intégration et Refactorisation des Modèles de Prédiction IA

- Intégration de nouveaux modèles de prédiction spécialisés.
- Refactorisation du script d'entraînement par ticker.
- Mise à jour du frontend pour les messages d'état d'entraînement.
- Ajout des scripts et résultats de backtesting.

## 016 - Améliorations et Débogage du Modèle de Prédiction IA

- Correction du chemin du module d'entraînement en arrière-plan.
- Capture des sorties d'entraînement pour le débogage.
- Résolution de la fuite de données et réentraînement du modèle.

## 015 - Correction des Imports et Refactorisation du Module Markets

- Correction des problèmes d'importation dans le backend Flask.
- Refactorisation du module `markets` et mise à jour des imports.
- Suppression des fichiers de test obsolètes.

## 014 - Refactorisation API, Marchés CSV et Intégration Modèle IA

- Refactorisation du backend Flask (architecture modulaire).
- Utilisation de fichiers CSV locaux pour les listes d'actions.
- Intégration d'un modèle de prédiction IA (Random Forest).
- Mise à jour du frontend Angular pour les nouvelles routes.

## 013 - Intégration d'un Modèle de Prédiction par IA

- Intégration d'une fonctionnalité de prédiction par Machine Learning.
- Script d'entraînement pour un modèle `RandomForestClassifier`.
- Création d'un service et d'une route API pour les prédictions.
- Mise à jour du frontend pour afficher signal et confiance.

## 012 - Passage aux Fichiers CSV Locaux pour les Listes d'Actions

- Remplacement de la récupération dynamique par des fichiers CSV locaux.
- Amélioration de la fiabilité et des performances.
- Simplification du code backend.

## 011 - Pluralisation des routes de l'API

- Mise à jour des routes de l'API de `/api/stock/` à `/api/stocks/`.
- Cohérence RESTful améliorée.
- Tests et service Angular mis à jour.

## 010 - Refactorisation de l'API Backend

- Refactorisation majeure du backend Flask (architecture modulaire).
- Séparation de la logique métier dans des services.
- Routes définies dans des Blueprints.
- Ajout de tests unitaires pour la couche de service.

## 009 - D��placement du dossier API

- Déplacement du dossier `api` dans `src/`.
- Meilleure organisation du projet.
- Mise à jour des chemins dans la documentation.

## 008 - Renommage de l'application en "TradeMind"

- Renommage complet de l'application.
- Reflète les objectifs futurs (analyse IA).
- Mise à jour des fichiers de configuration et du README.

## 007 - Ajout des cotations du CAC40

- Ajout de l'affichage des actions de l'indice CAC40.
- Création d'un nouvel endpoint API.
- Mise à jour de l'interface utilisateur.

## 006 - Recherche sur les intervalles yfinance

- Recherche sur les intervalles de temps `yfinance`.
- Échec de la recherche en raison de quotas.

## 005 - Ajout des tests unitaires pour le backend

- Ajout des tests unitaires pour le backend Flask.
- Correction des erreurs de sérialisation JSON et des mocks `yfinance`.

## 004 - Affichage des données historiques sur plusieurs périodes et intervalles

- Extension de l'affichage des données historiques (7j, 1m, 1a).
- Ajout des intervalles (1m, 5m, 15m, 30m, 1h).

## 003 - Affichage des données historiques avec intervalles 1m, 5m et 15m

- Extension de l'affichage des données historiques (1m, 5m, 15m).
- Concerne la dernière journée de cotation.

## 002 - Ajout des tests unitaires pour le backend

- Ajout des tests unitaires pour le backend Flask.

## 001 - Affichage des données historiques par intervalle de 15 minutes

- Ajout de l'affichage des données boursières par intervalle de 15 minutes.
- Concerne la dernière journée de cotation.
- Modification du backend Flask et du frontend Angular.