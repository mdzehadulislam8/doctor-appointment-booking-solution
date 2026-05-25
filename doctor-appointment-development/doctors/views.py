"""
Views for doctors app
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Doctor, Specialty, Hospital, Review, DoctorAvailability
from .forms import ReviewForm


def doctor_list(request):
    """List all doctors with filtering"""
    doctors = Doctor.objects.filter(is_verified=True, is_active=True)
    
    # Get filter parameters
    specialty_id = request.GET.get('specialty')
    hospital_id = request.GET.get('hospital')
    consultation_type = request.GET.get('type')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    search_query = request.GET.get('q', '')
    district = request.GET.get('district')
    
    # Apply filters
    if specialty_id:
        doctors = doctors.filter(specialties__id=specialty_id)
    
    if hospital_id:
        doctors = doctors.filter(hospitals__hospital__id=hospital_id)
    
    if district:
        doctors = doctors.filter(hospitals__hospital__district__icontains=district).distinct()
    
    if consultation_type == 'online':
        doctors = doctors.filter(consultation_fee_online__gt=0)
    elif consultation_type == 'in_person':
        doctors = doctors.filter(consultation_fee_in_person__gt=0)
    
    if min_price:
        doctors = doctors.filter(
            Q(consultation_fee_online__gte=min_price) |
            Q(consultation_fee_in_person__gte=min_price)
        )
    
    if max_price:
        doctors = doctors.filter(
            Q(consultation_fee_online__lte=max_price) |
            Q(consultation_fee_in_person__lte=max_price)
        )
    
    if search_query:
        doctors = doctors.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(specialties__name__icontains=search_query) |
            Q(hospitals__hospital__name__icontains=search_query) |
            Q(hospitals__hospital__city__icontains=search_query)
        ).distinct()
    
    # Pagination - 4 doctors per page
    paginator = Paginator(doctors, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all specialties and hospitals for filters
    specialties = Specialty.objects.filter(is_active=True)
    hospitals = Hospital.objects.filter(is_active=True)
    
    context = {
        'doctors': page_obj,
        'specialties': specialties,
        'hospitals': hospitals,
        'page_obj': page_obj,
        'paginator': paginator,
        'search_query': search_query,
    }
    
    return render(request, 'doctors/doctor_list.html', context)


def doctor_search(request):
    """Search doctors with advanced filtering"""
    return doctor_list(request)


def doctor_detail(request, pk):
    """Doctor profile detail view"""
    doctor = get_object_or_404(Doctor, pk=pk, is_verified=True, is_active=True)
    
    # Get reviews
    reviews = doctor.reviews.filter(is_active=True).select_related('patient')[:5]
    
    # Get availability for next 7 days
    from datetime import date, timedelta
    availabilities = DoctorAvailability.objects.filter(
        doctor=doctor,
        date__gte=date.today(),
        date__lte=date.today() + timedelta(days=7),
        is_available=True,
        is_booked=False
    ).order_by('date', 'time_slot')
    
    # Get hospitals
    hospitals = doctor.hospitals.filter(is_active=True)
    
    # Process qualifications - split by | if present
    qualifications_list = []
    if doctor.qualifications:
        qualifications_list = [q.strip() for q in doctor.qualifications.split('|')]
    else:
        qualifications_list = ["MBBS (DU)", "MD Cardiology (BSMMU)", "FACC (USA)"]
    
    # Check if in favorites
    is_favorite = False
    if request.user.is_authenticated and request.user.is_patient():
        try:
            is_favorite = doctor in request.user.patient_profile.favorite_doctors.all()
        except:
            pass
    
    context = {
        'doctor': doctor,
        'reviews': reviews,
        'availabilities': availabilities,
        'hospitals': hospitals,
        'qualifications_list': qualifications_list,
        'is_favorite': is_favorite,
    }
    
    return render(request, 'doctors/doctor_detail.html', context)


def doctor_reviews(request, pk):
    """View all reviews for a doctor"""
    doctor = get_object_or_404(Doctor, pk=pk, is_verified=True, is_active=True)
    reviews = doctor.reviews.filter(is_active=True).select_related('patient')
    
    # Pagination
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'doctor': doctor,
        'reviews': page_obj,
        'page_obj': page_obj,
    }
    
    return render(request, 'doctors/doctor_reviews.html', context)


@login_required
def add_review(request, pk):
    """Add a review for a doctor"""
    doctor = get_object_or_404(Doctor, pk=pk, is_verified=True, is_active=True)
    
    if not request.user.is_patient():
        messages.error(request, 'Only patients can add reviews.')
        return redirect('doctors:detail', pk=pk)
    
    # Check if user already reviewed
    if Review.objects.filter(doctor=doctor, patient=request.user).exists():
        messages.error(request, 'You have already reviewed this doctor.')
        return redirect('doctors:detail', pk=pk)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.doctor = doctor
            review.patient = request.user
            review.save()
            messages.success(request, 'Review added successfully!')
            return redirect('doctors:detail', pk=pk)
    else:
        form = ReviewForm()
    
    return render(request, 'doctors/add_review.html', {'form': form, 'doctor': doctor})


@login_required
def add_to_favorites(request, pk):
    """Add doctor to favorites"""
    doctor = get_object_or_404(Doctor, pk=pk, is_verified=True, is_active=True)
    
    if not request.user.is_patient():
        messages.error(request, 'Only patients can add favorites.')
        return redirect('doctors:detail', pk=pk)
    
    try:
        profile = request.user.patient_profile
        profile.favorite_doctors.add(doctor)
        messages.success(request, 'Doctor added to favorites!')
    except:
        messages.error(request, 'Could not add to favorites.')
    
    return redirect('doctors:detail', pk=pk)


@login_required
def remove_from_favorites(request, pk):
    """Remove doctor from favorites"""
    doctor = get_object_or_404(Doctor, pk=pk, is_verified=True, is_active=True)
    
    if not request.user.is_patient():
        messages.error(request, 'Only patients can manage favorites.')
        return redirect('doctors:detail', pk=pk)
    
    try:
        profile = request.user.patient_profile
        profile.favorite_doctors.remove(doctor)
        messages.success(request, 'Doctor removed from favorites.')
    except:
        messages.error(request, 'Could not remove from favorites.')
    
    return redirect('doctors:detail', pk=pk)


def doctors_by_specialty(request, specialty_slug):
    """List doctors by specialty"""
    specialty = get_object_or_404(Specialty, name__iexact=specialty_slug.replace('-', ' '))
    doctors = Doctor.objects.filter(specialties=specialty, is_verified=True, is_active=True)
    
    paginator = Paginator(doctors, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'specialty': specialty,
        'doctors': page_obj,
        'page_obj': page_obj,
    }
    
    return render(request, 'doctors/doctors_by_specialty.html', context)


def doctors_by_hospital(request, hospital_id):
    """List doctors by hospital"""
    hospital = get_object_or_404(Hospital, pk=hospital_id, is_active=True)
    doctors = Doctor.objects.filter(hospitals=hospital, is_verified=True, is_active=True)
    
    paginator = Paginator(doctors, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'hospital': hospital,
        'doctors': page_obj,
        'page_obj': page_obj,
    }
    
    return render(request, 'doctors/doctors_by_hospital.html', context)


def search_suggestions(request):
    """AJAX endpoint for search suggestions"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    # Search doctors
    doctors = Doctor.objects.filter(
        Q(user__first_name__icontains=query) |
        Q(user__last_name__icontains=query),
        is_verified=True,
        is_active=True
    )[:5]
    
    # Search specialties
    specialties = Specialty.objects.filter(
        name__icontains=query,
        is_active=True
    )[:3]
    
    # Search hospitals
    hospitals = Hospital.objects.filter(
        Q(name__icontains=query) |
        Q(city__icontains=query),
        is_active=True
    )[:3]
    
    suggestions = []
    
    for doctor in doctors:
        suggestions.append({
            'type': 'doctor',
            'id': doctor.id,
            'name': doctor.get_full_name(),
            'subtitle': doctor.get_primary_specialty().name if doctor.get_primary_specialty() else '',
            'url': f'/doctors/{doctor.id}/'
        })
    
    for specialty in specialties:
        suggestions.append({
            'type': 'specialty',
            'id': specialty.id,
            'name': specialty.name,
            'subtitle': 'Specialty',
            'url': f'/doctors/specialty/{specialty.name.lower().replace(" ", "-")}/'
        })
    
    for hospital in hospitals:
        suggestions.append({
            'type': 'hospital',
            'id': hospital.id,
            'name': hospital.name,
            'subtitle': f'{hospital.city}, {hospital.district}',
            'url': f'/doctors/hospital/{hospital.id}/'
        })
    
    return JsonResponse({'suggestions': suggestions})


def all_specialties(request):
    """Display all specialties in a grid/category view"""
    specialties = Specialty.objects.filter(is_active=True).order_by('order', 'name')
    
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
    
    # Enhance specialties with details
    for specialty in specialties:
        slug = specialty.name.lower().replace(" ", "-")
        if slug in specialty_details:
            specialty.emoji = specialty_details[slug]['emoji']
            specialty.description = specialty_details[slug]['description']
        else:
            specialty.emoji = '⚕️'
            specialty.description = f'{specialty.name} specialists'
    
    context = {
        'specialties': specialties,
    }
    
    return render(request, 'doctors/specialties_list.html', context)

