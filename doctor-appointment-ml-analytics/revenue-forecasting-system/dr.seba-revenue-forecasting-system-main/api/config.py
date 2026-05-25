"""
Configuration for the Commission Revenue Forecasting API
"""

from pathlib import Path

# API Version
API_VERSION = "1.0.0"

# Model path (relative to api folder)
MODEL_PATH = Path(__file__).parent.parent / 'models' / 'commission_revenue_forecasting_model.pkl'

# API Settings
API_HOST = "0.0.0.0"
API_PORT = 8000
LOG_LEVEL = "info"

# Forecast Settings
DEFAULT_FORECAST_DAYS = 30
MAX_FORECAST_DAYS = 365
MIN_FORECAST_DAYS = 1
