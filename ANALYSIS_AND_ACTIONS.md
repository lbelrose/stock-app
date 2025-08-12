# Analyse et Actions de l'Application TradeMind

## 1. Analyse de l'Architecture Initiale

### Objectif de l'Application
L'application est un traqueur d'actions en temps réel pour le Nasdaq Stock Exchange.

### Architecture Générale
L'application est une architecture client-serveur:
*   **Frontend:** Application web Angular (v19.2.0) avec Tailwind CSS pour le stylisme. Utilise `chart.js` et `ng2-charts` pour les graphiques.
*   **Backend:** API REST Flask (v3.0.3) en Python. Utilise `yfinance` pour récupérer les données boursières et `flask-cors` pour gérer les requêtes cross-origin. Le `README.md` mentionne l'utilisation de "TradingView API", mais l'implémentation actuelle utilise `yfinance`.

### Fonctionnalités Clés
*   Cotations boursières en temps réel du Nasdaq.
*   Graphiques boursiers interactifs avec plusieurs échelles de temps.
*   Fonctionnalité de recherche d'actions.
*   Gestion de la liste de surveillance (watchlist).
*   Indicateurs techniques (RSI, MACD).
*   Conception réactive pour tous les appareils.

### Communication
Le frontend Angular communique avec le backend Flask via des requêtes HTTP REST. `concurrently` est utilisé en développement pour lancer les deux serveurs simultanément.

### Points Forts
*   Séparation claire des préoccupations (frontend/backend).
*   Utilisation de frameworks modernes et populaires (Angular, Flask).
*   Intégration de `yfinance` pour les données boursières et calcul d'indicateurs techniques.

### Technologies Utilisées
*   Angular 19
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
├── src/                        # Angular frontend
│   ├── api/                    # Python backend
│   │   ├── stocks/             # Stocks feature module
│   │   │   ├── routes.py       # Blueprint for stock routes
│   │   │   ├── services.py     # Business logic for stocks
│   │   │   └── tests/          # Tests for the stocks module
│   │   ├── models/             # Data models and static files
│   │   │   └── markets/        # CSV files for markets
│   │   ├── app.py              # Flask application factory
│   │   ├── test_app.py         # Integration tests
│   │   └── requirements.txt    # Python dependencies
│   ├── app/                    # Application components
│   │   ├── features/           # Feature modules
│   │   └── shared/             # Shared components
│   └── assets/                 # Static assets
└── package.json                # Node.js dependencies
```

### Axes d'Amélioration (pour la production)
*   Ajouter l'authentification/autorisation.
*   Intégrer une base de données pour la persistance des données (ex: watchlist).
*   Améliorer la recherche d'actions (API externe ou base de données).
*   Mettre en place une gestion d'erreurs plus robuste.
*   Considérer le déploiement (WSGI, Docker, etc.).
*   Ajouter des tests unitaires et d'intégration.

## 2. Nouvelles Fonctionnalités

*   **Affichage des données historiques par intervalle de 15 minutes** (Voir CHANGELOG #001)
*   **Affichage des données historiques avec intervalles 1m, 5m et 15m** (Voir CHANGELOG #003)
*   **Affichage des données historiques sur plusieurs périodes et intervalles** (Voir CHANGELOG #004)
*   **Ajout des cotations du CAC40** (Voir CHANGELOG #007)

## 3. Actions Stratégiques

*   **Renommage de l'application en "TradeMind"** (Voir CHANGELOG #008)

## 4. Résolution des Problèmes

### Problème: Erreurs de récupération de données yfinance

**Description:** Le backend Flask rencontrait des erreurs `yfinance` (`No price data found`, `Expecting value: line 1 column 1 (char 0)`) lors de la récupération des données boursières pour divers symboles. Cela entraînait des réponses 404 de l'API.

**Résolution:** La mise à jour de la bibliothèque `yfinance` vers la dernière version (`0.2.64`) a résolu le problème. Il est recommandé de redémarrer le serveur backend après la mise à jour.

### Problème: Erreurs de sérialisation JSON et tests backend (Voir CHANGELOG #002)

**Description:** Les tests du backend échouaient en raison d'erreurs de sérialisation JSON (`Object of type int64 is not JSON serializable`) et de mocks `yfinance` incorrects.

**Résolution:** Conversion explicite des types numériques de NumPy en types Python standard dans les réponses JSON de l'API. Amélioration des mocks dans les tests pour simuler correctement les objets `pandas.DataFrame` et `datetime`.

### Licence
MIT

## 5. Intégration d'un module d'analyse par IA

**Objectif:** Ajouter une fonctionnalité d'analyse et de prédiction à l'application, en s'inspirant de projets de finance quantitative existants.

**Actions et Décisions:**

1.  **Analyse du projet `Alphon`:**
    - **Action:** Copie et analyse du projet `Alphon` dans `src/alphon_analysis`.
    - **Constat:** Le projet est une suite de recherche complète et très complexe, utilisant des modèles avancés (GNNs, Transformers) et un pipeline de données lourd. Il est inadapté à une intégration directe pour des prédictions en temps réel.
    - **Décision:** Ne pas intégrer `Alphon` directement, mais s'inspirer de sa logique de "featurization" (création d'indicateurs) pour construire un modèle plus simple.

2.  **Création d'un modèle de prédiction local:**
    - **Problème:** Le modèle simple (Random Forest) décrit dans le code d'`Alphon` n'était pas pr��sent dans les fichiers.
    - **Action:** Création d'un script d'entraînement dédié: `src/api/analysis/train_model.py`.
    - **Logique:** Le script télécharge l'historique d'une action (AAPL), calcule une série d'indicateurs techniques (SMA, EMA, RSI, MACD, etc.), et entraîne un modèle `RandomForestRegressor` de `scikit-learn` à prédire le rendement du jour suivant.
    - **Résultat:** Le modèle entraîné est sauvegardé dans `src/api/analysis/models/random_forest_model.joblib`.

3.  **Développement du Backend (Flask):**
    - **Action:** Création d'un nouveau module `analysis` dans `src/api`.
    - **Service:** `src/api/analysis/services.py` contient la `PredictionService` qui charge le modèle, récupère les dernières données pour un ticker, calcule les mêmes indicateurs, et retourne une prédiction.
    - **Route:** `src/api/analysis/routes.py` expose le service via l'endpoint `GET /api/analysis/<ticker>`.
    - **Intégration:** Le nouveau blueprint est enregistré dans `app.py`.

4.  **Développement du Frontend (Angular):**
    - **Action:** Mise à jour de `stock.model.ts` avec l'interface `StockPrediction`.
    - **Service:** `stock.service.ts` est enrichi d'une méthode `getPrediction(ticker)` qui appelle la nouvelle API.
    - **Composant:** `stock-detail.component.ts` appelle `getPrediction` et stocke le résultat.
    - **UI:** Le template de `stock-detail` affiche une nouvelle carte "AI Prediction" avec le signal (`BUY`/`SELL`/`HOLD`) et un score de confiance.
