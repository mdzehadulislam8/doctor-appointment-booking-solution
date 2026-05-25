"""
Forms for doctors app
"""
from django import forms
from .models import Review, Doctor, DoctorHospital


class ReviewForm(forms.ModelForm):
    """Review form"""
    
    rating = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Rating'
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Share your experience with this doctor...'
        }),
        label='Your Review'
    )
    
    class Meta:
        model = Review
        fields = ['rating', 'comment']


class DoctorProfileForm(forms.ModelForm):
    """Doctor profile update form"""
    
    class Meta:
        model = Doctor
        fields = [
            'qualifications', 'experience_years', 'about',
            'consultation_fee_online', 'consultation_fee_in_person',
            'profile_picture', 'cover_image'
        ]
        widgets = {
            'qualifications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'about': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'consultation_fee_online': forms.NumberInput(attrs={'class': 'form-control'}),
            'consultation_fee_in_person': forms.NumberInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control'}),
        }


class DoctorHospitalForm(forms.ModelForm):
    """Doctor hospital/chamber form"""
    
    class Meta:
        model = DoctorHospital
        fields = [
            'hospital', 'room_number', 'consultation_days',
            'morning_start', 'morning_end', 'evening_start', 'evening_end',
            'is_primary', 'is_active'
        ]
        widgets = {
            'hospital': forms.Select(attrs={'class': 'form-select'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control'}),
            'consultation_days': forms.CheckboxSelectMultiple(),
            'morning_start': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'morning_end': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'evening_start': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'evening_end': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
