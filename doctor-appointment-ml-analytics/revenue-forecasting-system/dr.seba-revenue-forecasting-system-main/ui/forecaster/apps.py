"""
App configuration for forecaster
"""
from django.apps import AppConfig


class ForecasterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'forecaster'
    verbose_name = 'Commission Revenue Forecaster'
