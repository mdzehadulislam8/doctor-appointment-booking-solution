"""
Admin configuration for payments app
"""
from django.contrib import admin
from .models import Payment, Invoice, DoctorEarning, Refund


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Payment Admin"""
    list_display = [
        'transaction_id', 'appointment', 'method', 'amount', 
        'status', 'created_at', 'completed_at'
    ]
    list_filter = ['method', 'status', 'created_at']
    search_fields = ['transaction_id', 'appointment__id', 'phone_number']
    date_hierarchy = 'created_at'


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """Invoice Admin"""
    list_display = [
        'invoice_number', 'appointment', 'total_amount', 
        'payment_method', 'created_at'
    ]
    search_fields = ['invoice_number', 'appointment__id', 'transaction_id']
    date_hierarchy = 'created_at'


@admin.register(DoctorEarning)
class DoctorEarningAdmin(admin.ModelAdmin):
    """Doctor Earning Admin"""
    list_display = [
        'doctor', 'appointment', 'total_amount', 'doctor_amount',
        'commission_rate', 'is_paid_to_doctor', 'month', 'year'
    ]
    list_filter = ['is_paid_to_doctor', 'month', 'year']
    search_fields = ['doctor__user__first_name', 'doctor__user__last_name']


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    """Refund Admin"""
    list_display = ['payment', 'amount', 'status', 'created_at', 'processed_at']
    list_filter = ['status', 'created_at']
