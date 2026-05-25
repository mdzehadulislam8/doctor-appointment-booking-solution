"""
Model Service - Load and cache CatBoost model
"""
import pickle as pk
import warnings
from functools import lru_cache
from pathlib import Path

from src.constants import MODEL_PATH
from src.config import CACHE_SIZE

warnings.filterwarnings('ignore')


@lru_cache(maxsize=CACHE_SIZE)
def load_model_package():
    """
    Load and cache the CatBoost model package
    
    Returns dict with:
        - model: CatBoost classifier
        - le_spec: specialization label encoder
        - le_hosp: hospital type label encoder
        - feature_encoders: dict of feature encoders
        - features: list of feature column names
    """
    with open(MODEL_PATH, 'rb') as f:
        package = pk.load(f)
    
    return {
        'model': package['model'],
        'le_spec': package['le_spec'],
        'le_hosp': package['le_hosp'],
        'feature_encoders': package['feature_encoders'],
        'features': package['features'],
    }


def predict_scores(x_temp, model):
    """
    Use model to predict scores for doctors
    
    Args:
        x_temp: Features dataframe
        model: CatBoost model
    
    Returns:
        numpy array of predicted scores
    """
    return model.predict(x_temp)
