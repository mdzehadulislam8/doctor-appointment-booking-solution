"""
Data Service - Load and process doctor data
"""
import warnings
from functools import lru_cache

import pandas as pd

from src.constants import DATA_PATH
from src.services.model_service import load_model_package
from src.config import CACHE_SIZE

warnings.filterwarnings('ignore')


@lru_cache(maxsize=CACHE_SIZE)
def load_doctor_data():
    """
    Load and preprocess doctor data from Excel
    
    Returns:
        DataFrame with doctors data
    """
    package = load_model_package()
    le_spec = package['le_spec']
    
    df = pd.read_excel(DATA_PATH)
    
    # Standardize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    
    # Binary encoding for Yes/No columns
    df['online_consultation'] = df['online_consultation'].map({'Yes': 1, 'No': 0}).fillna(0).astype(int)
    df['emergency_service'] = df['emergency_service'].map({'Yes': 1, 'No': 0}).fillna(0).astype(int)
    
    # Encode specialization
    df['specialization_group'] = le_spec.transform(df['specialization_group'].astype(str))
    
    return df


def get_options_data():
    """
    Get all available filter options
    
    Returns:
        dict with lists of districts, thanas, specializations
    """
    package = load_model_package()
    df = load_doctor_data()
    le_spec = package['le_spec']
    
    return {
        'districts': sorted(df['district'].unique().tolist()),
        'thanas': sorted(df['thana'].unique().tolist()),
        'specializations': sorted(le_spec.classes_.tolist()),
    }


def get_thanas_for_district(district):
    """
    Get thanas available in a district
    
    Args:
        district: District name
    
    Returns:
        Sorted list of thanas
    """
    df = load_doctor_data()
    return sorted(df[df['district'] == district]['thana'].unique().tolist())


def filter_doctors_by_criteria(df, district, thana, max_fee, online=0, emergency=0):
    """
    Filter doctors based on user criteria
    
    Args:
        df: Doctor dataframe
        district: Selected district
        thana: Selected thana
        max_fee: Maximum consultation fee
        online: 1 if online consultation required, 0 otherwise
        emergency: 1 if emergency service required, 0 otherwise
    
    Returns:
        Filtered dataframe
    """
    temp_df = df.copy()
    
    # Filter by location
    temp_df = temp_df[
        (temp_df['district'] == district) &
        (temp_df['thana'] == thana)
    ]
    
    # Filter by fee
    temp_df = temp_df[temp_df['consultation_fees'] <= max_fee]
    
    # Filter by services if requested
    if online == 1:
        temp_df = temp_df[temp_df['online_consultation'] == 1]
    
    if emergency == 1:
        temp_df = temp_df[temp_df['emergency_service'] == 1]
    
    return temp_df
