"""
URL patterns for dashboards app
"""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Main dashboard redirect
    path('', views.dashboard_index, name='index'),
    
    # Patient dashboard
    path('patient/', views.patient_dashboard, name='patient_dashboard'),
    
    # Doctor dashboard
    path('doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/profile/', views.doctor_profile, name='doctor_profile'),
    path('doctor/profile/edit/', views.doctor_profile_edit, name='doctor_profile_edit'),
    path('doctor/schedule/', views.doctor_schedule, name='doctor_schedule'),
    path('doctor/notifications/', views.doctor_notifications, name='doctor_notifications'),
    
    # Admin dashboard
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/<int:user_id>/update/', views.update_user, name='update_user'),
    path('admin/users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('admin/users/search/', views.search_users, name='search_users'),
    path('admin/employees/', views.admin_employees, name='admin_employees'),
    path('admin/employees/search/', views.search_employees, name='search_employees'),
    path('admin/employees/create/', views.create_employee, name='create_employee'),
    path('admin/employees/<int:employee_id>/update/', views.update_employee, name='update_employee'),
    path('admin/employees/<int:employee_id>/delete/', views.delete_employee, name='delete_employee'),
    path('admin/doctors/', views.admin_doctors, name='admin_doctors'),
    path('admin/doctors/<int:doctor_id>/', views.admin_doctor_detail, name='admin_doctor_detail'),
    path('admin/doctors/<int:doctor_id>/update/', views.update_doctor_details, name='update_doctor_details'),
    path('admin/doctors/<int:doctor_id>/schedule/<int:schedule_id>/update/', views.update_hospital_schedule, name='update_hospital_schedule'),
    path('admin/doctors/<int:doctor_id>/schedule/<int:schedule_id>/remove/', views.remove_doctor_hospital, name='remove_doctor_hospital'),
    path('admin/doctors/search/', views.search_doctors, name='search_doctors'),
    path('admin/hospitals/search/', views.search_hospitals, name='search_hospitals'),
    path('admin/doctors/verify/<int:doctor_id>/', views.verify_doctor, name='verify_doctor'),
    path('admin/doctors/toggle-status/<int:doctor_id>/', views.toggle_doctor_status, name='toggle_doctor_status'),
    path('admin/doctors/create/', views.create_doctor, name='create_doctor'),
    path('admin/hospitals/update/<int:hospital_id>/', views.update_hospital, name='update_hospital'),
    path('admin/hospitals/create/', views.create_hospital, name='create_hospital'),
    path('admin/appointments/', views.admin_appointments, name='admin_appointments'),
    path('admin/appointments/<int:appointment_id>/delete/', views.delete_appointment, name='delete_appointment'),
    path('admin/appointments/<int:appointment_id>/update/', views.update_appointment, name='update_appointment'),
    path('admin/appointments/search/', views.search_appointments, name='search_appointments'),
    path('admin/payments/', views.admin_payments, name='admin_payments'),
    path('admin/payments/<str:invoice_id>/flag/', views.flag_payment, name='flag_payment'),
    path('admin/payments/<str:invoice_id>/download/', views.download_invoice, name='download_invoice'),
    path('admin/payments/generate-bill/', views.generate_bill, name='generate_bill'),
    path('admin/payments/export-report/', views.export_report, name='export_report'),
    path('admin/payments/search/', views.search_payments, name='search_payments'),
    path('admin/statistics/', views.admin_statistics, name='admin_statistics'),
    
    # Employee dashboard
    path('employee/', views.employee_dashboard, name='employee_dashboard'),
    path('employee/appointments/', views.employee_appointments, name='employee_appointments'),
    path('employee/confirm/<int:appointment_id>/', views.employee_confirm_appointment, name='employee_confirm_appointment'),
]
