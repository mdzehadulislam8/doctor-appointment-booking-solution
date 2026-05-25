"""
Project constants and paths
"""
from pathlib import Path

# Base directory paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Root of project
MODEL_PATH = BASE_DIR / 'models' / 'doctor_ai_full_package.pkl'
DATA_PATH = BASE_DIR / 'data' / 'Dr.Seba_500_Organized_Final.xlsx'
DEMO_UI_DIR = BASE_DIR / 'demo_ui'

# Default values
DEFAULT_TOP_N = 5
DEFAULT_MAX_FEE = 2000

# Feature columns for model
FEATURE_NAMES = [
    'consultation_fees',
    'rating_avg',
    'experience_years',
    'online_consultation',
    'emergency_service',
    'hospital_type',
]
