"""
API Routes - URL patterns for Django
"""
from django.urls import path
from src.api import handlers

# API URL patterns
urlpatterns = [
    # HTML pages
    path('', handlers.home, name='home'),
    path('style.css', handlers.style_css, name='style-css'),
    
    # API endpoints
    path('api', handlers.api_root, name='api-root'),
    path('api/health', handlers.api_health, name='api-health'),
    path('api/options', handlers.api_options, name='api-options'),
    path('api/thanas/<str:district>', handlers.api_thanas, name='api-thanas'),
    path('api/recommendations', handlers.api_recommendations, name='api-recommendations'),
]
