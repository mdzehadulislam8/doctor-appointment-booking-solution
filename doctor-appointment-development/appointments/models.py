"""
Models for appointments app
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from doctors.models import Doctor, Hospital, DoctorAvailability


class Appointment(models.Model):
    """Appointment model"""
    
    # Status choices
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    # Consultation type
    CONSULTATION_TYPE = [
        ('online', 'Online'),
        ('in_person', 'In Person'),
    ]
    
    # Payment methods
    PAYMENT_METHODS = [
        ('bkash', 'bKash'),
        ('nagad', 'Nagad'),
        ('card', 'Credit/Debit Card'),
        ('cash', 'Cash on Arrival'),
    ]
    
    # Basic info
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='appointments')
    
    # Date and time
    date = models.DateField()
    time_slot = models.CharField(max_length=20)
    
    # Consultation details
    consultation_type = models.CharField(max_length=20, choices=CONSULTATION_TYPE, default='in_person')
    symptoms = models.TextField(blank=True, help_text="Patient's symptoms or reason for visit")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Fees
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Payment
    is_paid = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, blank=True)
    
    # Online consultation
    meeting_link = models.URLField(blank=True, help_text="Video call link for online consultations")
    
    # Notes
    doctor_notes = models.TextField(blank=True)
    patient_notes = models.TextField(blank=True)
    
    # Prescription
    prescription = models.TextField(blank=True)
    prescription_file = models.FileField(upload_to='prescriptions/', blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
        ordering = ['-date', '-time_slot']
    
    def __str__(self):
        return f"Appointment: {self.patient} with {self.doctor} on {self.date}"
    
    def calculate_total(self):
        """Calculate total amount safely with Decimal precision"""
        self.total_amount = (self.consultation_fee or Decimal('0')) + (self.service_fee or Decimal('0'))
        return self.total_amount
    
    def save(self, *args, **kwargs):
        # Calculate total if not set or is zero
        if self.total_amount is None or self.total_amount == 0:
            self.calculate_total()
        
        # Auto-set timestamps on status changes
        if self.status == 'confirmed' and not self.confirmed_at:
            self.confirmed_at = timezone.now()
        elif self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status == 'cancelled' and not self.cancelled_at:
            self.cancelled_at = timezone.now()
        
        super().save(*args, **kwargs)


class CartItem(models.Model):
    """Shopping cart for appointments"""
    
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart_items')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='cart_items')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='cart_items')
    availability = models.ForeignKey(DoctorAvailability, on_delete=models.CASCADE, related_name='cart_items')
    
    # Consultation details
    consultation_type = models.CharField(max_length=20, choices=Appointment.CONSULTATION_TYPE, default='in_person')
    symptoms = models.TextField(blank=True)
    
    # Fees
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['patient', 'availability'], name='unique_patient_availability')
        ]
    
    def __str__(self):
        return f"Cart: {self.patient} - {self.doctor}"
    
    def get_total(self):
        """Get total amount"""
        return self.consultation_fee + self.service_fee


class AppointmentHistory(models.Model):
    """History log for appointment status changes"""
    
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='history')
    status_from = models.CharField(max_length=20, blank=True)
    status_to = models.CharField(max_length=20)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Appointment History'
        verbose_name_plural = 'Appointment Histories'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.appointment} - {self.status_from} to {self.status_to}"
