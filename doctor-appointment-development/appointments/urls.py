"""
URL patterns for appointments app
"""
from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    # New multi-step booking
    path('book/<int:doctor_id>/', views.book_appointment, name='book_doctor'),
    path('confirmation/<int:appointment_id>/', views.confirmation, name='confirmation'),
    path('confirmation-guest/', views.confirmation_guest, name='confirmation_guest'),
    
    # Cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:availability_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    
    # Booking
    path('checkout/', views.checkout, name='checkout'),
    path('confirm/<int:appointment_id>/', views.confirm_appointment, name='confirm'),
    
    # Appointments
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('detail/<int:appointment_id>/', views.appointment_detail, name='detail'),
    path('cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel'),
    path('reschedule/<int:appointment_id>/', views.reschedule_appointment, name='reschedule'),
    
    # Doctor appointments
    path('doctor/appointments/', views.doctor_appointments, name='doctor_appointments'),
    path('doctor/confirm/<int:appointment_id>/', views.doctor_confirm, name='doctor_confirm'),
    path('doctor/complete/<int:appointment_id>/', views.doctor_complete, name='doctor_complete'),
    path('doctor/add-prescription/<int:appointment_id>/', views.add_prescription, name='add_prescription'),
    
    # API
    path('api/check-availability/', views.check_availability, name='check_availability'),
]
