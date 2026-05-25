"""
URL patterns for doctors app
"""
from django.urls import path
from . import views

app_name = 'doctors'

urlpatterns = [
    path('', views.doctor_list, name='list'),
    path('search/', views.doctor_search, name='search'),
    path('specialties/', views.all_specialties, name='all_specialties'),
    path('<int:pk>/', views.doctor_detail, name='detail'),
    path('<int:pk>/reviews/', views.doctor_reviews, name='reviews'),
    path('<int:pk>/add-review/', views.add_review, name='add_review'),
    path('<int:pk>/add-to-favorites/', views.add_to_favorites, name='add_to_favorites'),
    path('<int:pk>/remove-from-favorites/', views.remove_from_favorites, name='remove_from_favorites'),
    path('specialty/<str:specialty_slug>/', views.doctors_by_specialty, name='by_specialty'),
    path('hospital/<int:hospital_id>/', views.doctors_by_hospital, name='by_hospital'),
    path('api/search-suggestions/', views.search_suggestions, name='search_suggestions'),
]
