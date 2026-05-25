"""
Admin configuration for doctors app
"""
from django.contrib import admin
from .models import Specialty, Hospital, Doctor, DoctorHospital, Review, DoctorAvailability


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    """Specialty Admin"""
    list_display = ['name', 'name_bn', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['name', 'name_bn']
    ordering = ['order', 'name']


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    """Hospital Admin"""
    list_display = ['get_hospital_id', 'name', 'get_status_badge', 'phone', 'email', 'total_beds', 'icu_beds_available', 'get_doctors_count']
    list_filter = ['is_active', 'city', 'district']
    search_fields = ['name', 'address', 'city', 'district', 'phone', 'email']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'address', 'city', 'district')
        }),
        ('Contact Details', {
            'fields': ('phone', 'email', 'website')
        }),
        ('Facilities', {
            'fields': ('total_beds', 'icu_beds_available', 'logo')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_hospital_id(self, obj):
        return f"HOS-{obj.id:03d}"
    get_hospital_id.short_description = 'Hospital ID'
    
    def get_status_badge(self, obj):
        status = '✓ Active' if obj.is_active else '✗ Inactive'
        return status
    get_status_badge.short_description = 'Status'
    
    def get_doctors_count(self, obj):
        count = obj.doctors.count()
        return count
    get_doctors_count.short_description = 'Doctors'


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    """Doctor Admin"""
    list_display = ['get_doctor_id', 'get_full_name', 'get_age', 'get_primary_specialty_name', 'get_registration_date', 
                    'get_primary_hospital', 'get_consultation_fee', 'get_available_time', 'get_total_reviews', 
                    'get_commission_rate', 'get_status_badge', 'is_verified']
    list_filter = ['is_verified', 'is_active', 'specialties', 'experience_years', 'user__date_joined']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'bmdc_number']
    filter_horizontal = ['specialties']
    readonly_fields = ['created_at', 'updated_at', 'rating', 'total_reviews']
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'profile_picture', 'cover_image')
        }),
        ('Professional Details', {
            'fields': ('bmdc_number', 'specialties', 'qualifications', 'experience_years', 'about')
        }),
        ('Consultation Fees', {
            'fields': ('consultation_fee_online', 'consultation_fee_in_person', 'commission_rate')
        }),
        ('Verification & Status', {
            'fields': ('is_verified', 'verification_date', 'is_active')
        }),
        ('Rating & Reviews', {
            'fields': ('rating', 'total_reviews'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_doctor_id(self, obj):
        return f"DOC-{obj.id:03d}"
    get_doctor_id.short_description = 'Doctor ID'
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Doctor Name'
    
    def get_age(self, obj):
        """Get doctor's age from patient profile if available"""
        try:
            from accounts.models import PatientProfile
            if hasattr(obj.user, 'patient_profile') and obj.user.patient_profile.date_of_birth:
                from datetime import date
                dob = obj.user.patient_profile.date_of_birth
                age = (date.today() - dob).days // 365
                return age
        except:
            pass
        return "N/A"
    get_age.short_description = 'Age'
    
    def get_primary_specialty_name(self, obj):
        specialty = obj.get_primary_specialty()
        return specialty.name if specialty else "N/A"
    get_primary_specialty_name.short_description = 'Specialty'
    
    def get_registration_date(self, obj):
        return obj.created_at.strftime('%Y-%m-%d') if obj.created_at else "N/A"
    get_registration_date.short_description = 'Registration Date'
    
    def get_primary_hospital(self, obj):
        primary = obj.hospitals.filter(is_primary=True).first()
        if primary:
            return primary.hospital.name
        else:
            first = obj.hospitals.first()
            return first.hospital.name if first else "N/A"
    get_primary_hospital.short_description = 'Hospital'
    
    def get_consultation_fee(self, obj):
        return f"৳ {obj.consultation_fee_in_person}"
    get_consultation_fee.short_description = 'Consultation Fee'
    
    def get_available_time(self, obj):
        """Get available time from primary hospital"""
        primary = obj.hospitals.filter(is_primary=True).first()
        if primary:
            if primary.morning_start:
                return f"{primary.morning_start.strftime('%H:%M')} - {primary.morning_end.strftime('%H:%M')}"
        return "N/A"
    get_available_time.short_description = 'Available Time'
    
    def get_total_reviews(self, obj):
        return obj.total_reviews
    get_total_reviews.short_description = 'Patient Count'
    
    def get_commission_rate(self, obj):
        return f"{obj.commission_rate}%"
    get_commission_rate.short_description = 'Commission %'
    
    def get_status_badge(self, obj):
        if obj.is_verified and obj.is_active:
            return '✓ Active'
        elif obj.is_active:
            return '⊙ Pending'
        else:
            return '✗ Inactive'
    get_status_badge.short_description = 'Status'


@admin.register(DoctorHospital)
class DoctorHospitalAdmin(admin.ModelAdmin):
    """Doctor Hospital Admin"""
    list_display = ['doctor', 'hospital', 'room_number', 'is_primary', 'is_active']
    list_filter = ['is_primary', 'is_active']
    search_fields = ['doctor__user__first_name', 'doctor__user__last_name', 'hospital__name']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Review Admin"""
    list_display = ['doctor', 'patient', 'rating', 'is_active', 'created_at']
    list_filter = ['rating', 'is_active', 'created_at']
    search_fields = ['doctor__user__first_name', 'patient__username', 'comment']


@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    """Doctor Availability Admin"""
    list_display = ['doctor', 'hospital', 'date', 'time_slot', 'is_available', 'is_booked']
    list_filter = ['is_available', 'is_booked', 'date']
    search_fields = ['doctor__user__first_name', 'hospital__name']
    date_hierarchy = 'date'
