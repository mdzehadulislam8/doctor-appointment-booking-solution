"""
Configuration settings
"""
import os

# Debug mode
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# Cache settings
CACHE_SIZE = 1  # LRU cache max size for runtime data

# API settings
API_TIMEOUT = 30
MAX_RESULTS = 500

# Feature encoding
YES_NO_MAPPING = {'Yes': 1, 'No': 0}
