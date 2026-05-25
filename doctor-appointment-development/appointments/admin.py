"""
Admin configuration for appointments app
"""
from django.contrib import admin
from .models import Appointment, CartItem, AppointmentHistory


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """Appointment Admin"""
    list_display = [
        'id', 'patient', 'doctor', 'date', 'time_slot', 
        'consultation_type', 'status', 'is_paid', 'total_amount', 'created_at'
    ]
    list_filter = ['status', 'consultation_type', 'is_paid', 'date', 'created_at']
    search_fields = [
        'patient__username', 'patient__first_name', 
        'doctor__user__first_name', 'doctor__user__last_name'
    ]
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('patient', 'doctor', 'hospital')
        }),
        ('Schedule', {
            'fields': ('date', 'time_slot')
        }),
        ('Consultation', {
            'fields': ('consultation_type', 'symptoms', 'meeting_link')
        }),
        ('Status & Payment', {
            'fields': ('status', 'is_paid', 'payment_method')
        }),
        ('Fees', {
            'fields': ('consultation_fee', 'service_fee', 'total_amount')
        }),
        ('Notes', {
            'fields': ('doctor_notes', 'patient_notes')
        }),
        ('Prescription', {
            'fields': ('prescription', 'prescription_file')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'confirmed_at', 'completed_at', 'cancelled_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'confirmed_at', 'completed_at', 'cancelled_at']


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Cart Item Admin"""
    list_display = ['patient', 'doctor', 'hospital', 'consultation_type', 'get_total', 'created_at']
    list_filter = ['consultation_type', 'created_at']
    search_fields = ['patient__username', 'doctor__user__first_name']


@admin.register(AppointmentHistory)
class AppointmentHistoryAdmin(admin.ModelAdmin):
    """Appointment History Admin"""
    list_display = ['appointment', 'status_from', 'status_to', 'changed_by', 'created_at']
    list_filter = ['created_at']
    search_fields = ['appointment__id', 'changed_by__username']
