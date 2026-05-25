"""
URL patterns for accounts app
"""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/patient/', views.patient_register, name='patient_register'),
    path('register/doctor/', views.doctor_register, name='doctor_register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('password/change/', views.password_change, name='password_change'),
    path('language/<str:lang>/', views.set_language, name='set_language'),
    path('theme/<str:mode>/', views.set_theme, name='set_theme'),
]
