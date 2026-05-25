"""
User models for DrSeba.com
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class User(AbstractUser):
    """Custom User model with roles"""
    
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('admin', 'Super Admin'),
        ('employee', 'Employee'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    # Phone number - optional, any format, unique if provided
    phone = models.CharField(max_length=20, blank=True, null=True, unique=True)
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Language preference
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('bn', 'Bangla'),
    ]
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='en')
    
    # Dark mode preference
    dark_mode = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
    
    def is_patient(self):
        return self.role == 'patient'
    
    def is_doctor(self):
        return self.role == 'doctor'
    
    def is_super_admin(self):
        return self.role == 'admin'
    
    def is_employee(self):
        return self.role == 'employee'


class PatientProfile(models.Model):
    """Patient profile with additional information"""
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField(null=True, blank=True)
    
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    
    blood_group = models.CharField(max_length=5, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)
    medical_history = models.TextField(blank=True, help_text="Any existing medical conditions")
    allergies = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='patients/profiles/', blank=True, null=True)
    
    # Favorite doctors
    favorite_doctors = models.ManyToManyField('doctors.Doctor', blank=True, related_name='favorited_by')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Patient Profile'
        verbose_name_plural = 'Patient Profiles'
    
    def __str__(self):
        return f"Patient: {self.user.get_full_name() or self.user.username}"


class EmployeeProfile(models.Model):
    """Employee profile for staff members"""
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employee_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    joining_date = models.DateField()
    profile_picture = models.ImageField(upload_to='employees/profiles/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Employee Profile'
        verbose_name_plural = 'Employee Profiles'
    
    def __str__(self):
        return f"Employee: {self.user.get_full_name() or self.user.username}"


class PhoneVerification(models.Model):
    """Phone verification model for OTP"""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Phone Verification'
        verbose_name_plural = 'Phone Verifications'
    
    def __str__(self):
        return f"Verification for {self.phone}"
