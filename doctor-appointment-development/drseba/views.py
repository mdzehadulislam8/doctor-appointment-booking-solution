"""
Views for the main DrSeba app
"""
from django.shortcuts import render
from django.db.models import Count
from doctors.models import Specialty, Doctor, Review, Hospital


def home(request):
    """Home page view with popular specialties (only those with doctors)"""
    # Define specialty emojis and descriptions
    specialty_details = {
        'ayurvedic-unani-medicine': {'emoji': '🌿', 'description': 'Traditional herbal medicine specialists'},
        'ultrasonography': {'emoji': '📊', 'description': 'Ultrasound imaging specialists'},
        'cancer-medicine-tumor': {'emoji': '🎗️', 'description': 'Oncology and tumor treatment'},
        'gynecology-obstetrics': {'emoji': '🤰', 'description': 'Women\'s health and reproductive care'},
        'gastroenterology-liver': {'emoji': '🫀', 'description': 'Digestive system and liver specialists'},
        'ophthalmologist': {'emoji': '👁️', 'description': 'Eye care specialists'},
        'dermatology-allergy': {'emoji': '🩹', 'description': 'Skin, allergy and sexual health'},
        'thyroid-hormone-diabetes': {'emoji': '🦋', 'description': 'Endocrinology specialists'},
        'thalassemia-blood-cancer': {'emoji': '🩸', 'description': 'Blood disorders and adolescent care'},
        'dentist': {'emoji': '🦷', 'description': 'Dental care specialists'},
        'neonatal-pediatric': {'emoji': '👶', 'description': 'Newborn and child healthcare'},
        'ent-specialist': {'emoji': '👂', 'description': 'Ear, nose and throat specialists'},
        'neurology-neurosurgery': {'emoji': '🧠', 'description': 'Brain, nerve and stroke specialists'},
        'nutritionist-diet': {'emoji': '🥗', 'description': 'Diet and nutrition experts'},
        'physical-medicine': {'emoji': '🏃', 'description': 'Rehabilitation and physical therapy'},
        'orthopedics-trauma': {'emoji': '🦴', 'description': 'Bone, joint and trauma care'},
        'burn-plastic-cosmetic': {'emoji': '✂️', 'description': 'Reconstructive and cosmetic surgery'},
        'psychiatry-addiction': {'emoji': '🧘', 'description': 'Mental health and addiction treatment'},
        'medicine-heart-diabetes': {'emoji': '❤️', 'description': 'General medicine and cardiology'},
        'medicine-specialist': {'emoji': '💊', 'description': 'Internal medicine specialists'},
        'hematologist': {'emoji': '🩸', 'description': 'Blood disease specialists'},
        'general-surgeon': {'emoji': '🔪', 'description': 'General surgery specialists'},
        'cardiology': {'emoji': '❤️', 'description': 'Heart and cardiovascular specialists'},
        'dermatology': {'emoji': '🩹', 'description': 'Skin specialists'},
        'orthopedics': {'emoji': '🦴', 'description': 'Bone and joint specialists'},
        'neurology': {'emoji': '🧠', 'description': 'Neurological specialists'},
        'pediatrics': {'emoji': '👶', 'description': 'Child healthcare specialists'},
        'general-medicine': {'emoji': '💊', 'description': 'General medical practitioners'},
        'psychiatry': {'emoji': '🧘', 'description': 'Mental health specialists'},
        'surgery': {'emoji': '🔪', 'description': 'Surgical specialists'},
    }
    
    # Get specialties with doctors (has at least 1 doctor assigned)
    # Ordered by order field, then by doctor count
    specialties_with_doctors = Specialty.objects.filter(
        is_active=True,
        doctors__isnull=False  # Only specialties with doctors
    ).distinct().order_by('order', '-doctors__id').annotate(
        doctor_count=Count('doctors')
    )[:100]  # Get all but with reasonable limit
    
    # Limit to 8 for homepage display
    featured_specialties = list(specialties_with_doctors[:8])
    
    # Enhance specialties with emoji and descriptions
    for specialty in featured_specialties:
        slug = specialty.name.lower().replace(" ", "-")
        if slug in specialty_details:
            specialty.emoji = specialty_details[slug]['emoji']
            specialty.description = specialty_details[slug]['description']
        else:
            specialty.emoji = '⚕️'
            specialty.description = f'{specialty.name} specialists'
    
    total_specialties_with_doctors = specialties_with_doctors.count()
    show_see_all = total_specialties_with_doctors > 8
    
    # Get featured doctors (top 3 active doctors)
    featured_doctors = Doctor.objects.filter(is_active=True).order_by('-created_at')[:3]
    
    # Get featured reviews (top 3 recent reviews)
    featured_reviews = Review.objects.filter(is_active=True).order_by('-created_at')[:3]
    
    # Get partner hospitals (any active hospitals, limit to 3)
    partner_hospitals = Hospital.objects.filter(is_active=True).order_by('-created_at')[:3]
    
    context = {
        'featured_specialties': featured_specialties,
        'total_specialties_with_doctors': total_specialties_with_doctors,
        'show_see_all': show_see_all,
        'featured_doctors': featured_doctors,
        'featured_reviews': featured_reviews,
        'partner_hospitals': partner_hospitals,
    }
    
    return render(request, 'home.html', context)


def emergency(request):
    """Emergency services page"""
    return render(request, 'emergency.html')


def about(request):
    """About us page"""
    return render(request, 'about.html')
