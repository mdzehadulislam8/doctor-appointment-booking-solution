"""
URL patterns for payments app
"""
from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('process/<int:appointment_id>/', views.process_payment, name='process'),
    path('success/<int:payment_id>/', views.payment_success, name='success'),
    path('failed/<int:payment_id>/', views.payment_failed, name='failed'),
    path('history/', views.payment_history, name='history'),
    path('invoice/<int:invoice_id>/', views.view_invoice, name='view_invoice'),
    path('invoice/<int:invoice_id>/download/', views.download_invoice, name='download_invoice'),
    
    # Doctor earnings
    path('doctor/earnings/', views.doctor_earnings, name='doctor_earnings'),
    
    # Refund
    path('refund/request/<int:payment_id>/', views.request_refund, name='request_refund'),
]
