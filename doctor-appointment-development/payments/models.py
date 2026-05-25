"""
Models for payments app
"""
from django.db import models
from django.core.validators import MinValueValidator
import uuid


class Payment(models.Model):
    """Payment model"""
    
    # Payment methods
    PAYMENT_METHODS = [
        ('bkash', 'bKash'),
        ('nagad', 'Nagad'),
        ('card', 'Credit/Debit Card'),
        ('cash', 'Cash on Arrival'),
    ]
    
    # Status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    appointment = models.OneToOneField('appointments.Appointment', on_delete=models.CASCADE, related_name='payment')
    
    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Transaction details
    transaction_id = models.CharField(max_length=100, blank=True, unique=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    
    # For mobile payments (bKash/Nagad)
    phone_number = models.CharField(max_length=15, blank=True)
    
    # For card payments
    card_last_four = models.CharField(max_length=4, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment {self.transaction_id or self.id} - {self.get_method_display()}"
    
    def generate_transaction_id(self):
        """Generate unique transaction ID"""
        self.transaction_id = f"DRS{uuid.uuid4().hex[:12].upper()}"
        return self.transaction_id


class Invoice(models.Model):
    """Invoice model"""
    
    appointment = models.OneToOneField('appointments.Appointment', on_delete=models.CASCADE, related_name='invoice')
    
    # Invoice details
    invoice_number = models.CharField(max_length=50, unique=True)
    
    # Fee breakdown
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)
    service_fee = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment info
    payment_method = models.CharField(max_length=20, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    # PDF file
    pdf_file = models.FileField(upload_to='invoices/', blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invoice {self.invoice_number}"
    
    def generate_invoice_number(self):
        """Generate unique invoice number"""
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d')
        random_str = uuid.uuid4().hex[:6].upper()
        self.invoice_number = f"INV-{timestamp}-{random_str}"
        return self.invoice_number
    
    def calculate_total(self):
        """Calculate total amount"""
        self.total_amount = self.consultation_fee + self.service_fee + self.tax - self.discount
        return self.total_amount


class DoctorEarning(models.Model):
    """Doctor earnings/commission tracking"""
    
    doctor = models.ForeignKey('doctors.Doctor', on_delete=models.CASCADE, related_name='earnings')
    appointment = models.OneToOneField('appointments.Appointment', on_delete=models.CASCADE, related_name='doctor_earning')
    
    # Earnings breakdown
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    platform_commission = models.DecimalField(max_digits=10, decimal_places=2)
    doctor_amount = models.DecimalField(max_digits=10, decimal_places=2)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Status
    is_paid_to_doctor = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    
    # Month/Year for reporting
    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Doctor Earning'
        verbose_name_plural = 'Doctor Earnings'
        ordering = ['-created_at']
        unique_together = ['doctor', 'appointment']
    
    def __str__(self):
        return f"Earning: {self.doctor} - {self.doctor_amount}"
    
    def calculate_earnings(self):
        """Calculate doctor's earnings after commission"""
        self.platform_commission = (self.total_amount * self.commission_rate) / 100
        self.doctor_amount = self.total_amount - self.platform_commission
        return self.doctor_amount


class Refund(models.Model):
    """Refund model"""
    
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    
    # Refund details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    
    # Status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Refund transaction
    refund_transaction_id = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Refund'
        verbose_name_plural = 'Refunds'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Refund {self.id} - {self.amount}"
