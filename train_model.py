"""
Model Training & Comparison Script for Student Performance Prediction System
Trains, evaluates, and compares Linear Regression and Random Forest Regressor.
Saves the superior model and comprehensive evaluation metrics.
"""

import os
import json
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

FEATURE_COLUMNS = [
    "attendance",
    "internal_marks",
    "assignment_marks",
    "previous_marks",
    "study_hours",
    "activity_score"
]
TARGET_COLUMN = "final_marks"

def load_and_preprocess_data(csv_path: str):
    """Loads and preprocesses the student performance dataset."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"Dataset not found at '{csv_path}'. "
            "Please run 'python dataset/generate_dataset.py' to generate the dataset."
        )
    
    print(f"[1/6] Loading dataset from: {csv_path}")
    df = pd.read_csv(csv_path)
    
    print(f"      Initial shape: {df.shape[0]} rows, {df.shape[1]} columns")
    print("\n--- Dataset Info ---")
    print(df.info())
    print("\n--- First 5 Rows ---")
    print(df.head())
    
    # Check for missing values
    missing_count = df.isnull().sum().sum()
    print(f"\n[2/6] Checking for missing values: {missing_count} found.")
    if missing_count > 0:
        print("      Imputing missing values with column medians...")
        df = df.fillna(df.median(numeric_only=True))
    
    # Check and remove duplicates
    duplicate_count = df.duplicated().sum()
    print(f"      Checking for duplicate records: {duplicate_count} found.")
    if duplicate_count > 0:
        df = df.drop_duplicates().reset_index(drop=True)
        print(f"      Duplicates removed. New shape: {df.shape}")
    
    # Feature validation
    for col in FEATURE_COLUMNS + [TARGET_COLUMN]:
        if col not in df.columns:
            raise KeyError(f"Required column '{col}' is missing from the dataset!")
    
    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]
    
    print(f"\n[3/6] Features: {FEATURE_COLUMNS}")
    print(f"      Target: '{TARGET_COLUMN}'")
    
    return X, y, df

def evaluate_model(model, X_test, y_test, model_name: str) -> dict:
    """Evaluates regression model performance on the test set."""
    y_pred = model.predict(X_test)
    
    mae = float(mean_absolute_error(y_test, y_pred))
    mse = float(mean_squared_error(y_test, y_pred))
    rmse = float(np.sqrt(mse))
    r2 = float(r2_score(y_test, y_pred))
    
    return {
        "model_name": model_name,
        "mae": round(mae, 4),
        "mse": round(mse, 4),
        "rmse": round(rmse, 4),
        "r2_score": round(r2, 4)
    }

def train_and_compare_models(csv_path: str = None, models_dir: str = None):
    """Main training, evaluation, comparison, and persistence pipeline."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if csv_path is None:
        csv_path = os.path.join(base_dir, "dataset", "student_performance.csv")
    if models_dir is None:
        models_dir = os.path.join(base_dir, "models")
    
    os.makedirs(models_dir, exist_ok=True)
    
    # 1. Load & Preprocess
    X, y, df = load_and_preprocess_data(csv_path)
    
    # 2. Train-Test Split (80% Train, 20% Test)
    print("\n[4/6] Splitting dataset: 80% Training, 20% Testing (random_state=42)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )
    print(f"      Training samples: {X_train.shape[0]}, Testing samples: {X_test.shape[0]}")
    
    # 3. Model 1: Linear Regression
    print("\n[5/6] Training Candidate Models...")
    print("      -> Training Linear Regression...")
    lr_model = LinearRegression()
    lr_model.fit(X_train, y_train)
    lr_metrics = evaluate_model(lr_model, X_test, y_test, "Linear Regression")
    
    # 4. Model 2: Random Forest Regressor
    print("      -> Training Random Forest Regressor (n_estimators=120, max_depth=12)...")
    rf_model = RandomForestRegressor(
        n_estimators=120,
        max_depth=12,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    rf_model.fit(X_train, y_train)
    rf_metrics = evaluate_model(rf_model, X_test, y_test, "Random Forest Regressor")
    
    # 5. Comparison
    print("\n" + "=" * 68)
    print("                MODEL EVALUATION COMPARISON RESULTS")
    print("=" * 68)
    print(f"{'Metric':<20} | {'Linear Regression':<20} | {'Random Forest':<20}")
    print("-" * 68)
    print(f"{'MAE (Mean Abs Error)':<20} | {lr_metrics['mae']:<20.4f} | {rf_metrics['mae']:<20.4f}")
    print(f"{'MSE (Mean Sq Error)':<20} | {lr_metrics['mse']:<20.4f} | {rf_metrics['mse']:<20.4f}")
    print(f"{'RMSE (Root MSE)':<20} | {lr_metrics['rmse']:<20.4f} | {rf_metrics['rmse']:<20.4f}")
    print(f"{'R² Score (Variance)':<20} | {lr_metrics['r2_score']:<20.4f} | {rf_metrics['r2_score']:<20.4f}")
    print("=" * 68)
    
    # Select Best Model based on R2 Score (or lowest RMSE)
    if rf_metrics["r2_score"] >= lr_metrics["r2_score"]:
        best_model = rf_model
        best_model_name = "Random Forest Regressor"
        best_metrics = rf_metrics
    else:
        best_model = lr_model
        best_model_name = "Linear Regression"
        best_metrics = lr_metrics
    
    print(f"\n[6/6] Superior Model Selected: >>> {best_model_name} <<<")
    print(f"      Selected R² Score: {best_metrics['r2_score']:.4f} | RMSE: {best_metrics['rmse']:.4f}")
    
    # Calculate Feature Importances
    feature_importances = {}
    if hasattr(best_model, "feature_importances_"):
        for feat, imp in zip(FEATURE_COLUMNS, best_model.feature_importances_):
            feature_importances[feat] = round(float(imp), 4)
    elif hasattr(best_model, "coef_"):
        for feat, coef in zip(FEATURE_COLUMNS, best_model.coef_):
            feature_importances[feat] = round(float(coef), 4)
    
    # 6. Save Model and Metrics
    model_save_path = os.path.join(models_dir, "student_performance_model.pkl")
    metrics_save_path = os.path.join(models_dir, "model_metrics.json")
    
    joblib.dump(best_model, model_save_path)
    print(f"      Trained model saved to: {model_save_path}")
    
    summary_data = {
        "best_model_name": best_model_name,
        "features": FEATURE_COLUMNS,
        "target": TARGET_COLUMN,
        "dataset_samples": int(df.shape[0]),
        "train_samples": int(X_train.shape[0]),
        "test_samples": int(X_test.shape[0]),
        "linear_regression": lr_metrics,
        "random_forest": rf_metrics,
        "best_model_metrics": best_metrics,
        "feature_importances": feature_importances
    }
    
    with open(metrics_save_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=4)
    print(f"      Comparison metrics saved to: {metrics_save_path}")
    print("\nModel training and validation pipeline completed successfully!")

if __name__ == "__main__":
    train_and_compare_models()
