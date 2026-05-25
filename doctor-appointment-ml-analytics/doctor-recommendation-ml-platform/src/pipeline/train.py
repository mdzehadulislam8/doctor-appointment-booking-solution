"""
Doctor Recommendation Model Training Pipeline
===============================================

This script implements the complete training pipeline for the CatBoost doctor recommendation model.
It handles data loading, preprocessing, feature engineering, model training, and persistence.

Usage:
    python -m src.pipeline.train
    
Or:
    python src/pipeline/train.py

Output:
    - Trained model package saved to: models/doctor_ai_full_package.pkl
    - Model metrics saved to: artifacts/model_metrics.json
"""

import json
import logging
import pickle
from pathlib import Path
from typing import Dict, Tuple, Any

import numpy as np
import pandas as pd
from catboost import CatBoostRegressor
from sklearn.ensemble import GradientBoostingRegressor, AdaBoostRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MinMaxScaler

import xgboost as xgb

# ============================================================================
# CONFIGURATION
# ============================================================================

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_PATH = BASE_DIR / 'data' / 'Dr.Seba_500_Organized_Final.xlsx'
MODEL_OUTPUT_PATH = BASE_DIR / 'models' / 'doctor_ai_full_package.pkl'
METRICS_OUTPUT_PATH = BASE_DIR / 'artifacts' / 'model_metrics.json'

# Features used for training
FEATURES = [
    'experience_years',
    'consultation_fees',
    'rating_avg',
    'rating_count',
    'specialization_group',
    'hospital_type',
    'online_consultation',
    'emergency_service',
    'hospital_name',
    'district',
    'thana'
]

# Categorical features requiring label encoding
CATEGORICAL_FEATURES = ['hospital_name', 'district', 'thana']

# Model parameters
MODEL_PARAMS = {
    'catboost': {
        'iterations': 200,
        'learning_rate': 0.05,
        'depth': 4,
        'random_state': 42,
        'verbose': False
    },
    'xgboost': {
        'n_estimators': 200,
        'learning_rate': 0.05,
        'max_depth': 4,
        'random_state': 42
    },
    'gradient_boosting': {
        'n_estimators': 200,
        'learning_rate': 0.05,
        'max_depth': 4,
        'random_state': 42
    },
    'adaboost': {
        'n_estimators': 100,
        'learning_rate': 0.05,
        'random_state': 42
    }
}

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# DATA LOADING & PREPROCESSING
# ============================================================================

def load_data(data_path: Path) -> pd.DataFrame:
    """
    Load doctor data from Excel file.
    
    Args:
        data_path: Path to Excel file
    
    Returns:
        DataFrame with raw data
    
    Raises:
        FileNotFoundError: If data file not found
    """
    logger.info(f"Loading data from {data_path}")
    
    if not data_path.exists():
        raise FileNotFoundError(f"Data file not found: {data_path}")
    
    df = pd.read_excel(data_path)
    logger.info(f"Data loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    
    return df


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess raw data: standardize columns, handle missing values, encode binary features.
    
    Args:
        df: Raw dataframe
    
    Returns:
        Preprocessed dataframe
    """
    logger.info("Starting data preprocessing")
    
    df = df.copy()
    
    # Standardize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    logger.info("Column names standardized")
    
    # Handle missing values
    df['rating_avg'] = df['rating_avg'].fillna(df['rating_avg'].mean())
    df['experience_years'] = df['experience_years'].fillna(df['experience_years'].median())
    df['consultation_fees'] = df['consultation_fees'].fillna(df['consultation_fees'].median())
    df['rating_count'] = df['rating_count'].fillna(0)
    
    # Convert binary features
    df['online_consultation'] = df['online_consultation'].map({'Yes': 1, 'No': 0})
    df['emergency_service'] = df['emergency_service'].map({'Yes': 1, 'No': 0})
    
    # Drop rows with critical missing values
    df = df.dropna(subset=['specialization_group'])
    
    logger.info(f"After preprocessing: {df.shape[0]} rows")
    
    return df


def engineer_features(df: pd.DataFrame, scaler: MinMaxScaler = None) -> Tuple[pd.DataFrame, MinMaxScaler]:
    """
    Engineer new features for improved model performance.
    
    Features created:
        - rating_norm: Normalized rating (0-1)
        - experience_norm: Normalized experience (0-1)
        - reviews_log: Log-transformed review count
        - target_score: Composite score (50% rating + 30% experience + 20% reviews)
    
    Args:
        df: Preprocessed dataframe
        scaler: Existing scaler (for inference), None for training
    
    Returns:
        DataFrame with engineered features, scaler object
    """
    logger.info("Starting feature engineering")
    
    df = df.copy()
    
    # Create or use existing scaler
    if scaler is None:
        scaler = MinMaxScaler()
        df[['rating_norm', 'experience_norm']] = scaler.fit_transform(
            df[['rating_avg', 'experience_years']]
        )
    else:
        df[['rating_norm', 'experience_norm']] = scaler.transform(
            df[['rating_avg', 'experience_years']]
        )
    
    # Log transform reviews
    df['reviews_log'] = np.log1p(df['rating_count'])
    
    # Create composite target score
    df['target_score'] = (
        0.5 * df['rating_norm'] +
        0.3 * df['experience_norm'] +
        0.2 * df['reviews_log']
    )
    
    logger.info("Feature engineering complete")
    
    return df, scaler


def encode_categorical_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, LabelEncoder, LabelEncoder]:
    """
    Encode specialization and hospital type using label encoders.
    
    Args:
        df: Feature-engineered dataframe
    
    Returns:
        DataFrame with encoded features, specialization encoder, hospital encoder
    """
    logger.info("Encoding categorical features")
    
    df = df.copy()
    
    le_spec = LabelEncoder()
    le_hosp = LabelEncoder()
    
    df['specialization_group'] = le_spec.fit_transform(df['specialization_group'].astype(str))
    df['hospital_type'] = le_hosp.fit_transform(df['hospital_type'].astype(str))
    
    logger.info(f"Specializations: {len(le_spec.classes_)}, Hospitals: {len(le_hosp.classes_)}")
    
    return df, le_spec, le_hosp


# ============================================================================
# MODEL TRAINING
# ============================================================================

def split_data(X: pd.DataFrame, y: pd.Series, test_size: float = 0.2, random_state: int = 42) -> Tuple:
    """
    Split data into train/test sets.
    
    Args:
        X: Features
        y: Target
        test_size: Test set proportion
        random_state: Random seed
    
    Returns:
        X_train, X_test, y_train, y_test
    """
    logger.info(f"Splitting data: 80% train, 20% test")
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    
    logger.info(f"Train set: {X_train.shape}, Test set: {X_test.shape}")
    
    return X_train, X_test, y_train, y_test


def encode_train_test_features(X_train: pd.DataFrame, X_test: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, Dict]:
    """
    Encode categorical features in train/test sets using separate encoders per feature.
    
    Args:
        X_train: Training features
        X_test: Test features
    
    Returns:
        Encoded X_train, encoded X_test, feature encoders dictionary
    """
    logger.info("Encoding training/test feature columns")
    
    feature_encoders = {}
    
    for col in CATEGORICAL_FEATURES:
        le = LabelEncoder()
        
        # Fit on training data, transform both sets
        X_train[col] = le.fit_transform(X_train[col].astype(str))
        feature_encoders[col] = le
        
        # Transform test set, handle unseen values
        label_mapping = {label: idx for idx, label in enumerate(le.classes_)}
        X_test[col] = X_test[col].astype(str).map(label_mapping).fillna(-1).astype(int)
    
    logger.info(f"Encoded {len(feature_encoders)} categorical features")
    
    return X_train, X_test, feature_encoders


def train_models(X_train: pd.DataFrame, X_test: pd.DataFrame, y_train: pd.Series, y_test: pd.Series) -> Dict[str, Dict]:
    """
    Train multiple models and compare performance.
    
    Models trained:
        1. CatBoost (BEST - used in production)
        2. XGBoost
        3. Gradient Boosting
        4. AdaBoost
    
    Args:
        X_train, X_test: Features
        y_train, y_test: Targets
    
    Returns:
        Dictionary with model instances and metrics
    """
    logger.info("Training models...")
    
    results = {}
    
    # ========== CatBoost (PRODUCTION MODEL) ==========
    logger.info("Training CatBoost model")
    cat_model = CatBoostRegressor(**MODEL_PARAMS['catboost'])
    cat_model.fit(X_train, y_train)
    
    y_pred_cat = cat_model.predict(X_test)
    rmse_cat = np.sqrt(mean_squared_error(y_test, y_pred_cat))
    r2_cat = r2_score(y_test, y_pred_cat)
    
    results['catboost'] = {
        'model': cat_model,
        'rmse': rmse_cat,
        'r2': r2_cat
    }
    logger.info(f"CatBoost - RMSE: {rmse_cat:.4f}, R2: {r2_cat:.4f}")
    
    # ========== XGBoost ==========
    logger.info("Training XGBoost model")
    xgb_model = xgb.XGBRegressor(**MODEL_PARAMS['xgboost'])
    xgb_model.fit(X_train, y_train)
    
    y_pred_xgb = xgb_model.predict(X_test)
    rmse_xgb = np.sqrt(mean_squared_error(y_test, y_pred_xgb))
    r2_xgb = r2_score(y_test, y_pred_xgb)
    
    results['xgboost'] = {
        'model': xgb_model,
        'rmse': rmse_xgb,
        'r2': r2_xgb
    }
    logger.info(f"XGBoost - RMSE: {rmse_xgb:.4f}, R2: {r2_xgb:.4f}")
    
    # ========== Gradient Boosting ==========
    logger.info("Training Gradient Boosting model")
    gb_model = GradientBoostingRegressor(**MODEL_PARAMS['gradient_boosting'])
    gb_model.fit(X_train, y_train)
    
    y_pred_gb = gb_model.predict(X_test)
    rmse_gb = np.sqrt(mean_squared_error(y_test, y_pred_gb))
    r2_gb = r2_score(y_test, y_pred_gb)
    
    results['gradient_boosting'] = {
        'model': gb_model,
        'rmse': rmse_gb,
        'r2': r2_gb
    }
    logger.info(f"Gradient Boosting - RMSE: {rmse_gb:.4f}, R2: {r2_gb:.4f}")
    
    # ========== AdaBoost ==========
    logger.info("Training AdaBoost model")
    ada_model = AdaBoostRegressor(**MODEL_PARAMS['adaboost'])
    ada_model.fit(X_train, y_train)
    
    y_pred_ada = ada_model.predict(X_test)
    rmse_ada = np.sqrt(mean_squared_error(y_test, y_pred_ada))
    r2_ada = r2_score(y_test, y_pred_ada)
    
    results['adaboost'] = {
        'model': ada_model,
        'rmse': rmse_ada,
        'r2': r2_ada
    }
    logger.info(f"AdaBoost - RMSE: {rmse_ada:.4f}, R2: {r2_ada:.4f}")
    
    return results


def print_model_comparison(results: Dict[str, Dict]) -> None:
    """Print comparison of all trained models."""
    print("\n" + "="*60)
    print("MODEL PERFORMANCE COMPARISON")
    print("="*60)
    
    for model_name, data in results.items():
        print(f"\n{model_name.upper()}")
        print(f"  RMSE: {data['rmse']:.4f}")
        print(f"  R² Score: {data['r2']:.4f}")
    
    print("\n" + "="*60)
    print("✓ CATBOOST selected for production (best balance)")
    print("="*60 + "\n")


# ============================================================================
# MODEL PERSISTENCE
# ============================================================================

def save_model_package(best_model, le_spec: LabelEncoder, le_hosp: LabelEncoder, 
                       feature_encoders: Dict, features: list, output_path: Path) -> None:
    """
    Save complete model package (model + encoders + features) as pickle file.
    
    Args:
        best_model: Trained model
        le_spec: Specialization label encoder
        le_hosp: Hospital type label encoder
        feature_encoders: Dictionary of feature encoders
        features: List of feature names
        output_path: Path to save pickle file
    """
    logger.info(f"Saving model package to {output_path}")
    
    # Create output directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    model_package = {
        'model': best_model,
        'le_spec': le_spec,
        'le_hosp': le_hosp,
        'feature_encoders': feature_encoders,
        'features': features
    }
    
    with open(output_path, 'wb') as f:
        pickle.dump(model_package, f)
    
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    logger.info(f"Model package saved successfully ({file_size_mb:.2f} MB)")


def save_model_metrics(results: Dict[str, Dict], output_path: Path) -> None:
    """
    Save model performance metrics as JSON.
    
    Args:
        results: Dictionary of model results
        output_path: Path to save JSON file
    """
    logger.info(f"Saving metrics to {output_path}")
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    metrics = {
        model_name: {
            'rmse': float(data['rmse']),
            'r2': float(data['r2'])
        }
        for model_name, data in results.items()
    }
    
    with open(output_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    logger.info("Metrics saved successfully")


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def run_training_pipeline() -> None:
    """Execute complete training pipeline."""
    
    logger.info("="*70)
    logger.info("DOCTOR RECOMMENDATION MODEL - TRAINING PIPELINE")
    logger.info("="*70)
    
    try:
        # 1. Load data
        df = load_data(DATA_PATH)
        
        # 2. Preprocess
        df = preprocess_data(df)
        
        # 3. Feature engineering
        df, scaler = engineer_features(df)
        
        # 4. Encode specialization and hospital type
        df, le_spec, le_hosp = encode_categorical_features(df)
        
        # 5. Prepare features and target
        X = df[FEATURES]
        y = df['target_score']
        
        # 6. Train-test split
        X_train, X_test, y_train, y_test = split_data(X, y)
        
        # 7. Encode train/test features
        X_train, X_test, feature_encoders = encode_train_test_features(X_train, X_test)
        
        # 8. Train models
        results = train_models(X_train, X_test, y_train, y_test)
        
        # 9. Compare models
        print_model_comparison(results)
        
        # 10. Save best model (CatBoost)
        best_model = results['catboost']['model']
        save_model_package(best_model, le_spec, le_hosp, feature_encoders, FEATURES, MODEL_OUTPUT_PATH)
        
        # 11. Save metrics
        save_model_metrics(results, METRICS_OUTPUT_PATH)
        
        logger.info("="*70)
        logger.info("✓ TRAINING PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("="*70)
        
    except Exception as e:
        logger.error(f"Training pipeline failed: {str(e)}", exc_info=True)
        raise


if __name__ == '__main__':
    run_training_pipeline()
