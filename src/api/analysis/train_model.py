import pandas as pd
import numpy as np
import yfinance as yf
import os
import argparse

from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

from .features import generate_technical_features
from .models.model_factory import ModelFactory
from .optimize_threshold import optimize_thresholds


def train_model(ticker: str, model_class_name: str = "RandomForestModel", **model_kwargs):
    """
    Trains a classifier for a specific ticker using the modular architecture.
    """
    print(f"Starting training for {ticker} with model {model_class_name}...")

    # 1. Fetch data
    data = yf.Ticker(ticker).history(start="2015-01-01", end="2024-12-31")
    if data.empty:
        raise ValueError(f"No data found for {ticker}")
    data = data.sort_index(ascending=True)

    # 2. Generate features
    print("Generating features...")
    raw_features = generate_technical_features(data)

    # Target: 1 if tomorrow's close > today's close (good day to have bought)
    target = (data['Close'].shift(-1) > data['Close']).astype(int)

    # Lag features by one day (no leakage)
    lagged_features = raw_features.shift(1)
    model_df = lagged_features.copy()
    model_df['target'] = target
    model_df = model_df.dropna()

    if model_df.empty:
        print("Not enough data after processing.")
        return

    # Select only the 12 most interpretable and relevant features
    selected_features = [
        'return_lag_1',
        'return_lag_2',
        'return_lag_3',
        'volume_ratio_lag_1',
        'volume_ratio_lag_2',
        'volume_lag_1',
        'volume_lag_2',
        'close_sma10_ratio',
        'volatility_20',
        'rsi_lag_1',
        'return_1d',  # lagged via shift(1), so this is yesterday's return
        'return_5d'   # lagged
    ]

    # Safety check
    missing = [f for f in selected_features if f not in model_df.columns]
    if missing:
        print(f"Error: Missing features: {missing}")
        return

    X = model_df[selected_features]
    y = model_df['target']

    print(f"Using {len(X.columns)} features: {list(X.columns)}")
    print(f"Dataset size: {len(X)} samples")

    # Validate index
    if not X.index.equals(y.index):
        raise ValueError("Feature and target indices do not match.")
    if not X.index.is_monotonic_increasing:
        raise ValueError("Index is not sorted in ascending order.")

    # TimeSeriesSplit: Evaluate performance across multiple splits
    tscv = TimeSeriesSplit(n_splits=5)
    
    accuracies = []
    reports = []
    cms = []
    
    print("\n--- Starting Time Series Cross-Validation ---")
    for fold, (train_index, test_index) in enumerate(tscv.split(X)):
        print(f"\nFold {fold + 1}/{tscv.n_splits}")
        X_train_fold, X_test_fold = X.iloc[train_index], X.iloc[test_index]
        y_train_fold, y_test_fold = y.iloc[train_index], y.iloc[test_index]

        # Create a fresh model instance for each fold to avoid data leakage
        fold_model_instance = ModelFactory.create_model(model_class_name, ticker, selected_features, **model_kwargs)
        fold_model_instance.train(X_train_fold, y_train_fold)
        y_pred_fold = fold_model_instance.model.predict(X_test_fold)

        # Check if the test set has more than one class
        if len(np.unique(y_test_fold)) < 2:
            print(f"  Skipping metrics for fold {fold + 1} due to only one class present in the test set.")
            continue

        accuracy_fold = accuracy_score(y_test_fold, y_pred_fold)
        report_fold = classification_report(y_test_fold, y_pred_fold, target_names=["Down (0)", "Up (1)"], output_dict=True, zero_division=0)
        cm_fold = confusion_matrix(y_test_fold, y_pred_fold)

        accuracies.append(accuracy_fold)
        reports.append(report_fold)
        cms.append(cm_fold)

        print(f"  Accuracy: {accuracy_fold:.4f}")
        # print("  Classification Report:")
        # print(classification_report(y_test_fold, y_pred_fold, target_names=["Down (0)", "Up (1)"]))
        # print("  Confusion Matrix:")
        # print(cm_fold)

    print("\n--- Cross-Validation Summary ---")
    if not accuracies:
        print("Could not compute cross-validation metrics. All folds were skipped.")
    else:
        print(f"Average Accuracy: {np.mean(accuracies):.4f} (+/- {np.std(accuracies):.4f})")
        
        # Calculate average precision, recall, f1-score for class 1 (Up)
        avg_precision_up = np.mean([r['Up (1)']['precision'] for r in reports])
        avg_recall_up = np.mean([r['Up (1)']['recall'] for r in reports])
        avg_f1_up = np.mean([r['Up (1)']['f1-score'] for r in reports])
        
        print(f"Average Precision (Up): {avg_precision_up:.4f}")
        print(f"Average Recall (Up): {avg_recall_up:.4f}")
        print(f"Average F1-Score (Up): {avg_f1_up:.4f}")
    print("--------------------------------------------")

    # Re-run for the final model to be saved (using the last split for consistency with previous behavior)
    print("\n--- Final Model Training and Evaluation (Last Split) ---")
    X_train, X_test = X.iloc[train_index], X.iloc[test_index] # Use the last split
    y_train, y_test = y.iloc[train_index], y.iloc[test_index]

    print(f"Training size: {len(X_train)}, Test size: {len(X_test)}")

    # 3. Create and train model
    model_instance = ModelFactory.create_model(model_class_name, ticker, selected_features, **model_kwargs)
    model_instance.train(X_train, y_train)

    # 4. Evaluate model (using the internal sklearn model for metrics)
    if len(np.unique(y_test)) < 2:
        print("Skipping final evaluation because only one class is present in the test set.")
    else:
        y_pred = model_instance.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, target_names=["Down (0)", "Up (1)"], zero_division=0)
        cm = confusion_matrix(y_test, y_pred)

        print(f"Accuracy: {accuracy:.4f}")
        print("Classification Report:")
        print(report)
        print("Confusion Matrix:")
        print(cm)

    # Feature importance
    if hasattr(model_instance.model, 'feature_importances_'):
        importances = model_instance.model.feature_importances_
        importance_df = pd.DataFrame({
            'feature': X.columns,
            'importance': importances
        }).sort_values('importance', ascending=False)

        print("\nFeature Importance:")
        print(importance_df)

    # 5. Save model
    model_instance.save(directory=os.path.join(os.path.dirname(__file__), 'models'))

    # 6. Optimize and save the buy threshold for the newly trained model
    print(f"\n--- Optimizing Buy Threshold for {ticker} ---")
    try:
        optimize_thresholds(ticker_arg=ticker)
        print(f"--- Threshold optimization for {ticker} complete ---")
    except Exception as e:
        print(f"An error occurred during threshold optimization for {ticker}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train a buy signal classifier for a specific stock ticker.")
    parser.add_argument(
        '--ticker',
        type=str,
        required=True,
        help="The stock ticker symbol to train the model on (e.g., 'AAPL', 'MSFT')."
    )
    parser.add_argument(
        '--model_class',
        type=str,
        default="RandomForestModel",
        help="The class name of the model to train (e.g., 'RandomForestModel')."
    )
    
    # Parse known arguments, and collect the rest as model_kwargs
    args, unknown = parser.parse_known_args()

    model_kwargs = {}
    # Convert unknown arguments (e.g., --n_estimators 100) into a dictionary
    for i in range(0, len(unknown), 2):
        key = unknown[i].lstrip('--')
        value = unknown[i+1]
        # Attempt to convert to int or float if possible
        try:
            model_kwargs[key] = int(value)
        except ValueError:
            try:
                model_kwargs[key] = float(value)
            except ValueError:
                model_kwargs[key] = value

    ticker = args.ticker.upper()
    train_model(ticker=ticker, model_class_name=args.model_class, **model_kwargs)