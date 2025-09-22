# Analyse et Actions de l'Application TradeMind

## 1. Analyse de l'Architecture Initiale

### Objectif de l'Application
L'application est un traqueur d'actions en temps réel pour le Nasdaq Stock Exchange.

### Architecture Générale
L'application est une architecture client-serveur :
*   **Frontend :** Application web Angular (v21) utilisant Tailwind CSS. L'état est géré par les signaux Angular et les graphiques sont rendus avec `chart.js` et `ng2-charts`. L'architecture est modulaire, organisée en `features` (Dashboard, Stock-Detail) et `shared` (services, modèles, composants réutilisables).
*   **Backend :** API REST développée avec Flask (v3.0.3) en Python. Elle est structurée en modules (Blueprints) pour chaque domaine fonctionnel (stocks, markets, analysis). Elle utilise `yfinance` pour la récupération des données boursières et `scikit-learn` pour les modèles de prédiction.

### Fonctionnalités Clés
*   **Cotations boursières :** Affichage des données pour le CAC40 et le Nasdaq.
*   **Graphiques interactifs :** Visualisation des données historiques sur plusieurs périodes (1j, 7j, 1m, 1a) et intervalles (1m, 5m, 15m, 30m, 1h).
*   **Analyse par IA :** Prédiction de la tendance (hausse/baisse) basée sur un modèle de Machine Learning entraîné sur des indicateurs techniques.
*   **Gestion de watchlist :** Permet aux utilisateurs de suivre leurs actions préférées.
*   **Recherche d'actions :** Fonctionnalité de recherche simple.
*   **Responsive Design :** Interface adaptable à tous les appareils.

### Communication
Le frontend Angular communique avec le backend Flask via des requêtes HTTP REST. `concurrently` est utilisé en développement pour lancer les deux serveurs simultanément.

### Points Forts
*   Séparation claire des préoccupations (frontend/backend).
*   Utilisation de frameworks modernes et populaires (Angular, Flask).
*   Intégration de `yfinance` pour les données boursières et calcul d'indicateurs techniques.

### Technologies Utilisées
*   Angular 21
*   TailwindCSS
*   Python Flask
*   TradingView Technical Analysis Library (mentionné dans README, mais `yfinance` est utilisé dans le code)
*   Chart.js

### Prérequis et Installation
**Prérequis:**
*   Node.js 18.x ou supérieur
*   Python 3.8 ou supérieur
*   pip (gestionnaire de paquets Python)

**Installation:**
1.  Installer les dépendances Node.js:
    ```bash
    npm install
    ```
2.  Installer les dépendances Python:
    ```bash
    pip install -r src/api/requirements.txt
    ```

**Développement:**
Lancer le serveur de développement:
```bash
npm run dev
```
Ceci démarrera à la fois:
*   Le frontend Angular à `http://localhost:4200`
*   L'API Python à `http://localhost:5000`

### Structure du Projet
```
├── src/
│   ├── api/                    # Python backend (Flask)
│   │   ├── analysis/           # Analysis & Prediction module
│   │   │   ├── models/         # Trained AI models (.joblib)
│   │   │   ├── routes.py       # API routes for analysis
│   │   │   ├── services.py     # Business logic for predictions
│   │   │   └── train_model.py  # Model training script
│   │   ├── markets/            # Market data module
│   │   │   ├── models/         # Market data files (CSV)
│   │   │   ├── routes.py       # API routes for market lists
│   │   │   └── services.py     # Logic for reading market data
│   │   ├── stocks/             # Stock data module
│   │   │   ├── routes.py       # API routes for stock data
│   │   │   ├── services.py     # Logic for fetching stock data
│   │   │   └── tests/          # Unit tests for stock services
│   │   ├── api.py              # Flask application factory
│   │   └── requirements.txt    # Python dependencies
│   ├── app/                    # Angular frontend
│   │   ├── features/           # Feature modules
│   │   │   ├── dashboard/      # Dashboard component
│   │   │   └── stock-detail/   # Stock detail component
│   │   └── shared/             # Shared components, services, models
│   │       ├── components/     # Reusable UI components
│   │       ├── models/         # TypeScript models
│   │       └── services/       # Angular services
│   └── ...
└── package.json
```

### Axes d'Amélioration (pour la production)
*   Ajouter l'authentification/autorisation.
*   Intégrer une base de données pour la persistance des données (ex: watchlist).
*   Améliorer la recherche d'actions (API externe ou base de données).
*   Mettre en place une gestion d'erreurs plus robuste.
*   Considérer le déploiement (WSGI, Docker, etc.).
*   Ajouter des tests unitaires et d'intégration.

## 2. Évolutions et Fonctionnalités

*   **Visualisation des Données :** Mise en place de l'affichage des données historiques sur plusieurs périodes et intervalles pour une analyse détaillée (CHANGELOG #001, #003, #004).
*   **Extension des Marchés :** Ajout des cotations de l'indice CAC40 en plus du Nasdaq (CHANGELOG #007).
*   **Intégration de l'IA :** Développement d'un module de prédiction (Random Forest) pour anticiper les tendances du marché. Le backend a été doté d'un service et d'une route API dédiée, et le frontend mis à jour pour afficher ces prédictions (CHANGELOG #014).
*   **Refactorisation Backend :** L'API Flask a été restructurée pour être plus modulaire (Blueprints) et utilise désormais des fichiers CSV locaux pour une meilleure fiabilité des listes d'actions (CHANGELOG #014).
*   **Mise à Jour Frontend :** L'application a été migrée vers Angular 21. Les composants principaux ont été refactorisés avec des fichiers dédiés et l'état est maintenant géré par les signaux Angular pour une meilleure performance (CHANGELOG #019).
*   **Refactorisation Frontend (Templates/Styles & Signals) :** Migration des templates et styles inline vers des fichiers dédiés pour `StockCardComponent` et `StockSearchComponent`. Conversion des propriétés réactives en `signals` pour `StockCardComponent` (`isInWatchlist`) et `StockSearchComponent` (`searchQuery`, `searchResults`, `showResults`). Application de `ChangeDetectionStrategy.OnPush` pour `StockSearchComponent` (CHANGELOG #021).
*   **Amélioration UX :** Le marché par défaut est maintenant le CAC40 pour une expérience plus pertinente pour les utilisateurs français.

*   **Intégration Frontend des Scripts Génériques d'Entraînement et de Prédiction :** Le frontend Angular a été mis à jour pour interagir avec les nouveaux endpoints de l'API Flask. `stock.service.ts` a été modifié pour appeler les routes d'entraînement et de prédiction génériques, et `stock-detail.component.ts` inclut désormais un bouton pour déclencher l'entraînement du modèle, avec un affichage de l'état de chargement (CHANGELOG #028).
*   **Intégration des Scripts Génériques dans l'API Flask :** L'API Flask a été mise à jour pour intégrer les scripts génériques d'entraînement et de prédiction. De nouveaux endpoints (`/api/analysis/train/<ticker>` et `/api/analysis/predict/<ticker>`) ont été ajoutés, et la classe `PredictionService` a été renommée en `AnalysisService` pour gérer ces opérations de manière modulaire (CHANGELOG #027).
*   **Scripts d'Entraînement et de Prédiction Génériques :** Des scripts génériques ont été introduits pour l'entraînement (`generic_train_all_models.py`) et la prédiction (`predict_next_day.py`) des modèles IA. Un fichier `model_configs.json` centralise les hyperparamètres, et `optimized_thresholds.json` inclut désormais le nom de la classe de modèle pour chaque ticker, rendant l'architecture plus flexible et extensible (CHANGELOG #026).
*   **Amélioration de l'Évaluation du Modèle avec Validation Croisée Temporelle :** Le script d'entraînement (`train_model.py`) a été mis à jour pour inclure une évaluation plus robuste via la validation croisée temporelle. Cela permet de calculer et d'afficher les métriques de performance (précision, rappel, F1-score, exactitude) pour chaque split, ainsi que leurs moyennes, offrant une meilleure compréhension de la généralisation du modèle (CHANGELOG #025).
*   **Amélioration des Métriques de Backtesting :** Le script de backtesting a été enrichi avec de nouvelles métriques clés : la Précision Directionnelle, le Drawdown Maximal et le Ratio de Sharpe, offrant une évaluation plus complète de la performance et du risque de la stratégie (CHANGELOG #023).
*   **Re-exécution des Backtests :** Les backtests ont ��té re-exécutés pour tous les tickers sur la période du 1er semestre 2025 en utilisant les seuils optimisés. Les résultats ont été sauvegardés et les problèmes d'importation dans le script de backtesting ont été résolus (CHANGELOG #022).

## 3. Actions Stratégiques

*   **Renommage de l'application :** L'application a été renommée "TradeMind" pour mieux refléter son orientation vers l'analyse intelligente des données boursières (CHANGELOG #008).

## 4. Intégration d'un module d'analyse par IA

**Objectif:** Ajouter une fonctionnalité d'analyse et de prédiction à l'application.

**Actions et Décisions:**
1.  **Analyse du projet `Alphon`:** Non intégré directement, inspiration pour la "featurization".
2.  **Modularisation de l'Architecture des Modèles :**
    - Création d'une classe abstraite `BaseModel` (`src/api/analysis/models/base_model.py`) pour définir une interface commune (entraînement, prédiction, sauvegarde, chargement).
    - Implémentation d'une classe de modèle concrète `RandomForestModel` (`src/api/analysis/models/random_forest_model.py`) héritant de `BaseModel`.
    - Création d'un `ModelFactory` (`src/api/analysis/models/model_factory.py`) pour l'instanciation dynamique des modèles.
3.  **Scripts Génériques d'Entraînement et de Prédiction :**
    - Création de `model_configs.json` pour centraliser les hyperparamètres des différents types de modèles.
    - Création de `generic_train_all_models.py` pour orchestrer l'entraînement de tous les modèles.
    - Création de `predict_next_day.py` pour effectuer des prédictions en utilisant la nouvelle architecture.
4.  **Intégration des Scripts Génériques dans l'API Flask :**
    - Modification de `src/api/analysis/routes.py` pour ajouter des endpoints pour l'entraînement et la prédiction génériques.
    - Renommage de la classe `PredictionService` en `AnalysisService` dans `src/api/analysis/services.py` et implémentation des méthodes `train_model_generic` et `get_prediction_generic`.
5.  **Intégration Frontend des Scripts Génériques d'Entraînement et de Prédiction :**
    - Mise à jour de `src/app/shared/services/stock.service.ts` pour appeler les nouveaux endpoints d'entraînement et de prédiction.
    - Modification de `src/app/features/stock-detail/stock-detail.component.ts` et `src/app/features/stock-detail/stock-detail.component.html` pour intégrer la fonctionnalité d'entraînement et l'affichage des prédictions.
6.  **Création et Intégration d'un modèle de prédiction local:**
    - Le script d'entraînement (`train_model.py`) a été adapté pour utiliser la nouvelle architecture modulaire, permettant de créer et d'entraîner des modèles via le `ModelFactory`.
    - Le script de backtesting (`backtest.py`) a également été adapté pour charger et utiliser les modèles via la nouvelle architecture, en tirant parti de `BaseModel.load` et `ModelFactory`.
    - Backend Flask: Nouveau module `analysis` avec `PredictionService` et route API. La fonction `get_prediction` persiste chaque modèle spécialisé généré pour une utilisation ultérieure. Le script `predict_next_day.py` utilise désormais les seuils d'achat optimisés par ticker, chargés depuis `optimized_thresholds.json`.
    - Frontend Angular: Mise à jour de `stock.model.ts`, `stock.service.ts` et `stock-detail.component.ts` pour afficher les prédictions.
7.  **Gestion des Modèles :** Le répertoire `src/api/analysis/models/` est maintenant suivi par Git pour versionner les modèles entraînés avec le code source.

## 5. Résolution des Problèmes

### Problème: Erreurs de récupération de données yfinance

**Description:** Le backend Flask rencontrait des erreurs `yfinance` (`No price data found`, `Expecting value: line 1 column 1 (char 0)`) lors de la récupération des données boursières pour divers symboles. Cela entraînait des réponses 404 de l'API.

**Résolution:** La mise à jour de la bibliothèque `yfinance` vers la dernière version (`0.2.64`) a résolu le problème. Il est recommandé de redémarrer le serveur backend après la mise à jour.

### Problème: Erreurs de sérialisation JSON et tests backend (Voir CHANGELOG #002)

**Description:** Les tests du backend échouaient en raison d'erreurs de sérialisation JSON (`Object of type int64 is not JSON serializable`) et de mocks `yfinance` incorrects.

**Résolution:** Conversion explicite des types numériques de NumPy en types Python standard dans les réponses JSON de l'API. Amélioration des mocks dans les tests pour simuler correctement les objets `pandas.DataFrame` et `datetime`.

### Problème: ModuleNotFoundError lors de l'entraînement en arrière-plan

**Description:** Le processus d'entraînement du modèle spécialisé en arrière-plan échouait avec une `ModuleNotFoundError: No module named 'src.api'`.

**Résolution:** Le sous-processus `train_model.py` était exécuté avec un contexte de module incorrect. La correction a consisté à lancer le sous-processus depuis la racine du projet en spécifiant le paramètre `cwd` dans `subprocess.Popen`.

### Licence
MIT