"""
Views for dashboards app
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from django.http import JsonResponse
from datetime import date, timedelta
import string
import secrets

from accounts.models import User, PatientProfile, EmployeeProfile
from doctors.models import Doctor, Specialty, Hospital, Review, DoctorHospital
from appointments.models import Appointment, CartItem
from payments.models import Payment, Invoice, DoctorEarning


def dashboard_index(request):
    """Redirect to appropriate dashboard based on user role"""
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    if request.user.is_super_admin():
        return redirect('dashboard:admin_dashboard')
    elif request.user.is_doctor():
        return redirect('dashboard:doctor_dashboard')
    elif request.user.is_employee():
        return redirect('dashboard:employee_dashboard')
    else:
        return redirect('dashboard:patient_dashboard')


# Patient Dashboard
@login_required
def patient_dashboard(request):
    """Patient dashboard"""
    if not request.user.is_patient():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # Get patient profile
    try:
        profile = request.user.patient_profile
    except PatientProfile.DoesNotExist:
        profile = PatientProfile.objects.create(user=request.user)
    
    # Upcoming appointments
    upcoming_appointments = Appointment.objects.filter(
        patient=request.user,
        date__gte=date.today(),
        status__in=['pending', 'confirmed']
    ).order_by('date', 'time_slot')[:5]
    
    # Past appointments
    past_appointments = Appointment.objects.filter(
        patient=request.user,
        status__in=['completed', 'cancelled']
    ).order_by('-date')[:5]
    
    # Cart items
    cart_items = CartItem.objects.filter(patient=request.user)
    
    # Favorite doctors
    favorite_doctors = profile.favorite_doctors.all()[:4]
    
    # Recent payments
    recent_payments = Payment.objects.filter(
        appointment__patient=request.user,
        status='completed'
    ).order_by('-created_at')[:5]
    
    context = {
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
        'cart_count': cart_items.count(),
        'favorite_doctors': favorite_doctors,
        'recent_payments': recent_payments,
        'profile': profile,
    }
    
    return render(request, 'dashboards/patient_dashboard.html', context)


# Doctor Dashboard
@login_required
def doctor_dashboard(request):
    """Doctor dashboard"""
    if not request.user.is_doctor():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    try:
        doctor = request.user.doctor_profile
    except:
        messages.error(request, 'Doctor profile not found.')
        return redirect('home')
    
    # Today's appointments
    today_appointments = Appointment.objects.filter(
        doctor=doctor,
        date=date.today()
    ).order_by('time_slot')
    
    # Upcoming appointments
    upcoming_count = Appointment.objects.filter(
        doctor=doctor,
        date__gt=date.today(),
        status__in=['pending', 'confirmed']
    ).count()
    
    # Total patients
    total_patients = Appointment.objects.filter(
        doctor=doctor,
        status='completed'
    ).values('patient').distinct().count()
    
    # Rating
    rating = doctor.rating
    total_reviews = doctor.total_reviews
    
    # Monthly earnings
    from django.db.models import Sum
    current_month = timezone.now().month
    current_year = timezone.now().year
    
    monthly_earnings = DoctorEarning.objects.filter(
        doctor=doctor,
        month=current_month,
        year=current_year
    ).aggregate(total=Sum('doctor_amount'))['total'] or 0
    
    # Recent reviews
    recent_reviews = Review.objects.filter(
        doctor=doctor,
        is_active=True
    ).select_related('patient').order_by('-created_at')[:5]
    
    context = {
        'doctor': doctor,
        'today_appointments': today_appointments,
        'upcoming_count': upcoming_count,
        'total_patients': total_patients,
        'rating': rating,
        'total_reviews': total_reviews,
        'monthly_earnings': monthly_earnings,
        'recent_reviews': recent_reviews,
    }
    
    return render(request, 'dashboards/doctor_dashboard.html', context)


@login_required
def doctor_profile(request):
    """Doctor profile view"""
    if not request.user.is_doctor():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    try:
        doctor = request.user.doctor_profile
    except:
        messages.error(request, 'Doctor profile not found.')
        return redirect('home')
    
    context = {
        'doctor': doctor,
    }
    
    return render(request, 'dashboards/doctor_profile.html', context)


@login_required
def doctor_profile_edit(request):
    """Edit doctor profile"""
    if not request.user.is_doctor():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    try:
        doctor = request.user.doctor_profile
    except:
        messages.error(request, 'Doctor profile not found.')
        return redirect('home')
    
    from doctors.forms import DoctorProfileForm
    
    if request.method == 'POST':
        form = DoctorProfileForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('dashboard:doctor_profile')
    else:
        form = DoctorProfileForm(instance=doctor)
    
    context = {
        'form': form,
        'doctor': doctor,
    }
    
    return render(request, 'dashboards/doctor_profile_edit.html', context)


@login_required
def doctor_schedule(request):
    """Doctor schedule management"""
    if not request.user.is_doctor():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    try:
        doctor = request.user.doctor_profile
    except:
        messages.error(request, 'Doctor profile not found.')
        return redirect('home')
    
    from doctors.models import DoctorHospital
    
    hospitals = DoctorHospital.objects.filter(doctor=doctor)
    
    context = {
        'hospitals': hospitals,
    }
    
    return render(request, 'dashboards/doctor_schedule.html', context)


@login_required
def doctor_notifications(request):
    """Doctor notifications"""
    if not request.user.is_doctor():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # Mock notifications (in production, use a proper notification system)
    notifications = [
        {
            'message': 'New appointment booked',
            'time': '2 hours ago',
            'is_read': False,
        },
        {
            'message': 'Appointment cancelled by patient',
            'time': '5 hours ago',
            'is_read': True,
        },
    ]
    
    context = {
        'notifications': notifications,
    }
    
    return render(request, 'dashboards/doctor_notifications.html', context)


# Admin Dashboard
@login_required
def admin_dashboard(request):
    """Super admin dashboard"""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # Statistics
    total_doctors = Doctor.objects.count()
    total_patients = User.objects.filter(role='patient').count()
    total_appointments = Appointment.objects.count()
    total_revenue = Payment.objects.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # Pending verifications
    pending_verifications = Doctor.objects.filter(is_verified=False).count()
    
    # Recent appointments
    recent_appointments = Appointment.objects.order_by('-created_at')[:10]
    
    # Today's appointments
    today_appointments = Appointment.objects.filter(date=date.today()).count()
    
    # Monthly revenue chart data
    from django.db.models.functions import TruncMonth
    
    monthly_revenue = Payment.objects.filter(
        status='completed'
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')[:12]
    
    context = {
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'total_revenue': total_revenue,
        'pending_verifications': pending_verifications,
        'recent_appointments': recent_appointments,
        'today_appointments': today_appointments,
        'monthly_revenue': monthly_revenue,
    }
    
    return render(request, 'dashboards/admin_dashboard.html', context)


@login_required
def admin_users(request):
    """Admin user management"""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    users = User.objects.all().order_by('-date_joined')
    
    context = {
        'users': users,
    }
    
    return render(request, 'dashboards/admin_users.html', context)


@login_required
def admin_employees(request):
    """Admin employees management"""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    employees = User.objects.filter(role='employee').order_by('-date_joined')
    
    # Handle search filter
    search_query = request.GET.get('search', '').strip()
    if search_query:
        employees = employees.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    context = {
        'employees': employees,
        'search_query': search_query,
    }
    
    return render(request, 'dashboards/admin_employees.html', context)


@login_required
def search_employees(request):
    """Autocomplete search for employees"""
    if not request.user.is_super_admin():
        return JsonResponse({'success': False, 'results': []})
    
    query = request.GET.get('q', '').strip()
    
    if len(query) < 1:
        return JsonResponse({'success': True, 'results': []})
    
    employees = User.objects.filter(
        role='employee',
    ).filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(email__icontains=query) |
        Q(phone__icontains=query)
    ).values('id', 'first_name', 'last_name', 'email', 'phone', 'date_joined')[:10]
    
    results = []
    for emp in employees:
        full_name = f"{emp['first_name']} {emp['last_name']}"
        results.append({
            'id': emp['id'],
            'name': full_name,
            'email': emp['email'],
            'phone': emp['phone'] or 'N/A',
            'display': f"{full_name} ({emp['email']})"
        })
    
    return JsonResponse({'success': True, 'results': results})


@login_required
def search_doctors(request):
    """Autocomplete search for doctors"""
    if not request.user.is_super_admin():
        return JsonResponse({'success': False, 'results': []})
    
    query = request.GET.get('q', '').strip()
    
    if len(query) < 1:
        return JsonResponse({'success': True, 'results': []})
    
    doctors = Doctor.objects.filter(
        Q(user__first_name__icontains=query) |
        Q(user__last_name__icontains=query) |
        Q(user__email__icontains=query) |
        Q(bmdc_number__icontains=query)
    ).select_related('user', 'specialty').values('id', 'user__first_name', 'user__last_name', 'user__email', 'specialty__name')[:10]
    
    results = []
    for doc in doctors:
        full_name = f"Dr. {doc['user__first_name']} {doc['user__last_name']}"
        results.append({
            'id': doc['id'],
            'name': full_name,
            'email': doc['user__email'],
            'specialty': doc['specialty__name'] or 'N/A',
            'display': f"{full_name} - {doc['specialty__name']}"
        })
    
    return JsonResponse({'success': True, 'results': results})


@login_required
def search_hospitals(request):
    """Autocomplete search for hospitals"""
    if not request.user.is_super_admin():
        return JsonResponse({'success': False, 'results': []})
    
    query = request.GET.get('q', '').strip()
    
    if len(query) < 1:
        return JsonResponse({'success': True, 'results': []})
    
    hospitals = Hospital.objects.filter(
        Q(name__icontains=query) |
        Q(phone__icontains=query) |
        Q(email__icontains=query)
    ).values('id', 'name', 'phone', 'email', 'city')[:10]
    
    results = []
    for hosp in hospitals:
        results.append({
            'id': hosp['id'],
            'name': hosp['name'],
            'phone': hosp['phone'] or 'N/A',
            'city': hosp['city'] or 'N/A',
            'display': f"{hosp['name']} - {hosp['city']}"
        })
    
    return JsonResponse({'success': True, 'results': results})


@login_required
def search_appointments(request):
    """Autocomplete search for appointments"""
    if not request.user.is_super_admin():
        return JsonResponse({'success': False, 'results': []})
    
    query = request.GET.get('q', '').strip()
    
    if len(query) < 1:
        return JsonResponse({'success': True, 'results': []})
    
    appointments = Appointment.objects.filter(
        Q(patient__first_name__icontains=query) |
        Q(patient__last_name__icontains=query) |
        Q(doctor__user__first_name__icontains=query) |
        Q(doctor__user__last_name__icontains=query)
    ).select_related('patient', 'doctor').values('id', 'patient__first_name', 'patient__last_name', 'doctor__user__first_name', 'doctor__user__last_name', 'date', 'status')[:10]
    
    results = []
    for appt in appointments:
        patient_name = f"{appt['patient__first_name']} {appt['patient__last_name']}"
        doctor_name = f"Dr. {appt['doctor__user__first_name']} {appt['doctor__user__last_name']}"
        results.append({
            'id': appt['id'],
            'patient': patient_name,
            'doctor': doctor_name,
            'date': str(appt['date']),
            'status': appt['status'],
            'display': f"{patient_name} - {doctor_name} ({appt['date']})"
        })
    
    return JsonResponse({'success': True, 'results': results})


@login_required
def search_payments(request):
    """Autocomplete search for payments"""
    if not request.user.is_super_admin():
        return JsonResponse({'success': False, 'results': []})
    
    query = request.GET.get('q', '').strip()
    
    if len(query) < 1:
        return JsonResponse({'success': True, 'results': []})
    
    payments = Payment.objects.filter(
        Q(appointment__patient__first_name__icontains=query) |
        Q(appointment__patient__last_name__icontains=query) |
        Q(appointment__doctor__user__first_name__icontains=query) |
        Q(appointment__doctor__user__last_name__icontains=query)
    ).select_related('appointment').values('id', 'appointment__patient__first_name', 'appointment__patient__last_name', 'appointment__doctor__user__first_name', 'appointment__doctor__user__last_name', 'amount', 'created_at')[:10]
    
    results = []
    for pay in payments:
        patient_name = f"{pay['appointment__patient__first_name']} {pay['appointment__patient__last_name']}"
        doctor_name = f"Dr. {pay['appointment__doctor__user__first_name']} {pay['appointment__doctor__user__last_name']}"
        results.append({
            'id': pay['id'],
            'patient': patient_name,
            'doctor': doctor_name,
            'amount': str(pay['amount']),
            'date': str(pay['created_at'].date()),
            'display': f"{patient_name} - {doctor_name} (৳{pay['amount']})"
        })
    
    return JsonResponse({'success': True, 'results': results})


@login_required
def search_users(request):
    """Autocomplete search for users"""
    if not request.user.is_super_admin():
        return JsonResponse({'success': False, 'results': []})
    
    query = request.GET.get('q', '').strip()
    
    if len(query) < 1:
        return JsonResponse({'success': True, 'results': []})
    
    users = User.objects.filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(email__icontains=query)
    ).values('id', 'first_name', 'last_name', 'email', 'is_super_admin', 'is_doctor', 'is_employee', 'is_patient')[:10]
    
    results = []
    for user in users:
        role = []
        if user['is_super_admin']:
            role.append('Admin')
        if user['is_doctor']:
            role.append('Doctor')
        if user['is_employee']:
            role.append('Employee')
        if user['is_patient']:
            role.append('Patient')
        
        role_str = ', '.join(role) if role else 'User'
        full_name = f"{user['first_name']} {user['last_name']}"
        
        results.append({
            'id': user['id'],
            'name': full_name,
            'email': user['email'],
            'role': role_str,
            'display': f"{full_name} ({user['email']}) - {role_str}"
        })
    
    return JsonResponse({'success': True, 'results': results})


@login_required
def admin_doctors(request):
    """Admin doctor management"""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    doctors = Doctor.objects.all().order_by('-created_at')
    hospitals = Hospital.objects.all().order_by('-created_at')
    
    context = {
        'doctors': doctors,
        'hospitals': hospitals,
    }
    
    return render(request, 'dashboards/admin_doctors.html', context)


@login_required
def verify_doctor(request, doctor_id):
    """Verify doctor account"""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    doctor = get_object_or_404(Doctor, id=doctor_id)
    
    doctor.is_verified = True
    doctor.verification_date = timezone.now()
    doctor.save()
    
    messages.success(request, f'Doctor {doctor.get_full_name()} has been verified.')
    return redirect('dashboard:admin_doctors')


@login_required
def toggle_doctor_status(request, doctor_id):
    """Toggle doctor active/inactive status"""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    doctor = get_object_or_404(Doctor, id=doctor_id)
    doctor.is_active = not doctor.is_active
    doctor.save()
    
    status = "activated" if doctor.is_active else "deactivated"
    messages.success(request, f'Doctor {doctor.get_full_name()} has been {status}.')
    return redirect('dashboard:admin_doctors')


@login_required
def update_hospital(request, hospital_id):
    """Update hospital information"""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    hospital = get_object_or_404(Hospital, id=hospital_id)
    
    if request.method == 'POST':
        hospital.name = request.POST.get('hospital_name', hospital.name)
        hospital.city = request.POST.get('location', hospital.city)
        hospital.phone = request.POST.get('contact_number', hospital.phone)
        hospital.email = request.POST.get('email', hospital.email)
        hospital.total_beds = request.POST.get('total_beds', hospital.total_beds)
        hospital.icu_beds_available = request.POST.get('icu_beds', hospital.icu_beds_available)
        hospital.is_active = request.POST.get('status') == 'active'
        hospital.save()
        
        messages.success(request, f'Hospital {hospital.name} has been updated successfully.')
        return redirect('dashboard:admin_doctors')
    
    return redirect('dashboard:admin_doctors')


@login_required
def admin_doctor_detail(request, doctor_id):
    """Admin doctor detail view with edit capabilities"""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    doctor = get_object_or_404(Doctor, id=doctor_id)
    hospital_schedules = doctor.hospitals.all().select_related('hospital')
    
    context = {
        'doctor': doctor,
        'hospital_schedules': hospital_schedules,
    }
    
    return render(request, 'dashboards/admin_doctor_detail.html', context)


@login_required
def update_doctor_details(request, doctor_id):
    """Update doctor basic information"""
    if not request.user.is_super_admin():
        return JsonResponse({'success': False, 'message': 'Access denied.'})
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method.'})
    
    doctor = get_object_or_404(Doctor, id=doctor_id)
    
    try:
        # Update doctor information
        user = doctor.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.phone = request.POST.get('phone', user.phone)
        user.save()
        
        # Update doctor-specific fields
        doctor.bmdc_number = request.POST.get('bmdc_number', doctor.bmdc_number)
        doctor.experience_years = request.POST.get('experience_years', doctor.experience_years)
        doctor.qualifications = request.POST.get('qualifications', doctor.qualifications)
        doctor.is_verified = request.POST.get('is_verified') == 'on'
        doctor.is_active = request.POST.get('is_active') == 'on'
        doctor.save()
        
        return JsonResponse({'success': True, 'message': 'Doctor updated successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
def update_hospital_schedule(request, doctor_id, schedule_id):
    """Update doctor's hospital schedule"""
    if not request.user.is_super_admin():
        return JsonResponse({'success': False, 'message': 'Access denied.'})
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method.'})
    
    doctor = get_object_or_404(Doctor, id=doctor_id)
    schedule = get_object_or_404(DoctorHospital, id=schedule_id, doctor=doctor)
    
    try:
        # Parse consultation days (comma-separated)
        days_str = request.POST.get('consultation_days', '')
        days = [day.strip() for day in days_str.split(',') if day.strip()]
        
        schedule.consultation_days = days
        
        # Update time slots
        if request.POST.get('morning_start'):
            schedule.morning_start = request.POST.get('morning_start')
        if request.POST.get('morning_end'):
            schedule.morning_end = request.POST.get('morning_end')
        if request.POST.get('evening_start'):
            schedule.evening_start = request.POST.get('evening_start')
        if request.POST.get('evening_end'):
            schedule.evening_end = request.POST.get('evening_end')
        
        schedule.save()
        
        return JsonResponse({'success': True, 'message': 'Schedule updated successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
def remove_doctor_hospital(request, doctor_id, schedule_id):
    """Remove hospital from doctor's schedule"""
    if not request.user.is_super_admin():
        return JsonResponse({'success': False, 'message': 'Access denied.'})
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method.'})
    
    doctor = get_object_or_404(Doctor, id=doctor_id)
    schedule = get_object_or_404(DoctorHospital, id=schedule_id, doctor=doctor)
    
    try:
        hospital_name = schedule.hospital.name
        schedule.delete()
        return JsonResponse({'success': True, 'message': f'{hospital_name} removed successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
def create_doctor(request):
    """Create new doctor"""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if request.method == 'POST':
        try:
            # Create user account
            email = request.POST.get('email')
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            
            # Check if user already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered.')
                return redirect('dashboard:admin_doctors')
            
            # Create user
            user = User.objects.create_user(
                email=email,
                username=email,
                first_name=first_name,
                last_name=last_name,
                password='DoctorTemp123!@#'  # Temporary password
            )
            user.is_doctor = True
            user.save()
            
            # Create doctor profile
            doctor = Doctor.objects.create(
                user=user,
                bmdc_number=request.POST.get('bmdc_number'),
                experience_years=int(request.POST.get('experience_years', 0)),
                qualifications=request.POST.get('qualification', ''),
                consultation_fee_online=float(request.POST.get('consultation_fee_online', 0)),
                consultation_fee_in_person=float(request.POST.get('consultation_fee_in_person', 0)),
                is_active=request.POST.get('status') == 'active'
            )
            
            # Add specialty
            specialty_id = request.POST.get('specialty')
            if specialty_id:
                try:
                    specialty = Specialty.objects.get(id=specialty_id)
                    doctor.specialties.add(specialty)
                except Specialty.DoesNotExist:
                    pass
            
            # Add hospital if selected
            hospital_id = request.POST.get('hospital')
            if hospital_id:
                try:
                    hospital = Hospital.objects.get(id=hospital_id)
                    DoctorHospital.objects.create(
                        doctor=doctor,
                        hospital=hospital,
                        is_primary=True
                    )
                except Hospital.DoesNotExist:
                    pass
            
            messages.success(request, f'Doctor {user.get_full_name()} created successfully. Temporary password: DoctorTemp123!@#')
            return redirect('dashboard:admin_doctors')
            
        except Exception as e:
            messages.error(request, f'Error creating doctor: {str(e)}')
            return redirect('dashboard:admin_doctors')
    
    return redirect('dashboard:admin_doctors')


@login_required
def create_hospital(request):
    """Create new hospital"""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if request.method == 'POST':
        try:
            hospital = Hospital.objects.create(
                name=request.POST.get('hospital_name'),
                address=request.POST.get('address', ''),
                city=request.POST.get('location', ''),
                phone=request.POST.get('contact_number', ''),
                email=request.POST.get('email', ''),
                website=request.POST.get('website', ''),
                total_beds=int(request.POST.get('total_beds', 0)),
                icu_beds_available=int(request.POST.get('icu_beds', 0)),
                is_active=request.POST.get('status') == 'active'
            )
            
            messages.success(request, f'Hospital {hospital.name} created successfully.')
            return redirect('dashboard:admin_doctors')
            
        except Exception as e:
            messages.error(request, f'Error creating hospital: {str(e)}')
            return redirect('dashboard:admin_doctors')
    
    return redirect('dashboard:admin_doctors')


@login_required
def create_employee(request):
    """Create new employee"""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            phone = request.POST.get('phone')
            department = request.POST.get('department')
            designation = request.POST.get('designation')
            joining_date = request.POST.get('joining_date')
            is_active = request.POST.get('is_active') == 'on'
            
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, 'An account with this email already exists.')
                return redirect('dashboard:admin_employees')
            
            # Generate temporary password
            temp_password = 'Emp' + ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10)) + '!@#'
            
            # Create User account
            user = User.objects.create_user(
                username=email.split('@')[0] + str(secrets.randbelow(10000)),
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                role='employee',
                password=temp_password
            )
            
            # Create EmployeeProfile
            employee_id = f'EMP-{user.id:04d}'
            EmployeeProfile.objects.create(
                user=user,
                employee_id=employee_id,
                department=department,
                designation=designation,
                joining_date=joining_date,
                is_active=is_active
            )
            
            messages.success(request, f'Employee {user.get_full_name()} created successfully. Temporary password: {temp_password}')
            return redirect('dashboard:admin_employees')
            
        except Exception as e:
            messages.error(request, f'Error creating employee: {str(e)}')
            return redirect('dashboard:admin_employees')
    
    return redirect('dashboard:admin_employees')


@login_required
def update_employee(request, employee_id):
    """Update employee"""
    if not request.user.is_super_admin():
        return JsonResponse({'success': False, 'message': 'Access denied.'})
    
    if request.method == 'POST':
        try:
            user = User.objects.get(id=employee_id)
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.phone = request.POST.get('phone', user.phone)
            user.save()
            
            return JsonResponse({'success': True, 'message': 'Employee updated successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def delete_employee(request, employee_id):
    """Delete employee"""
    if not request.user.is_super_admin():
        return JsonResponse({'success': False, 'message': 'Access denied.'})
    
    if request.method == 'POST':
        try:
            user = User.objects.get(id=employee_id)
            user.delete()
            return JsonResponse({'success': True, 'message': 'Employee deleted successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def update_user(request, user_id):
    """Update user"""
    if not request.user.is_super_admin():
        return JsonResponse({'success': False, 'message': 'Access denied.'})
    
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.phone = request.POST.get('phone', user.phone)
            user.role = request.POST.get('role', user.role)
            user.save()
            
            return JsonResponse({'success': True, 'message': 'User updated successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def delete_user(request, user_id):
    """Delete user"""
    if not request.user.is_super_admin():
        return JsonResponse({'success': False, 'message': 'Access denied.'})
    
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return JsonResponse({'success': True, 'message': 'User deleted successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def delete_appointment(request, appointment_id):
    """Delete appointment"""
    if not request.user.is_super_admin():
        return JsonResponse({'success': False, 'message': 'Access denied.'})
    
    if request.method == 'POST':
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            appointment.delete()
            return JsonResponse({'success': True, 'message': 'Appointment deleted successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def update_appointment(request, appointment_id):
    """Update appointment details"""
    if not request.user.is_super_admin():
        return JsonResponse({'success': False, 'message': 'Access denied.'})
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method.'})
    
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        
        # Update appointment information
        if request.POST.get('date'):
            appointment.date = request.POST.get('date')
        if request.POST.get('time_slot'):
            appointment.time_slot = request.POST.get('time_slot')
        if request.POST.get('service_charge'):
            appointment.service_fee = request.POST.get('service_charge')
        if request.POST.get('notes'):
            appointment.patient_notes = request.POST.get('notes')
        if request.POST.get('status'):
            appointment.status = request.POST.get('status')
        
        appointment.save()
        return JsonResponse({'success': True, 'message': 'Appointment updated successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
def flag_payment(request, invoice_id):
    """Flag payment"""
    if not request.user.is_super_admin():
        return JsonResponse({'success': False, 'message': 'Access denied.'})
    
    if request.method == 'POST':
        try:
            reason = request.POST.get('reason')
            notes = request.POST.get('notes', '')
            
            # In a real application, this would update a Payment/Invoice model
            # For now, we'll just return success
            return JsonResponse({'success': True, 'message': f'Payment flagged as {reason}'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def generate_bill(request):
    """Generate bill for doctor"""
    if not request.user.is_super_admin():
        return JsonResponse({'success': False, 'message': 'Access denied.'})
    
    if request.method == 'POST':
        try:
            doctor_id = request.POST.get('doctor')
            from_date = request.POST.get('from_date')
            to_date = request.POST.get('to_date')
            
            # In a real application, this would generate a PDF
            messages.success(request, f'Bill generated for date range {from_date} to {to_date}')
            return JsonResponse({'success': True, 'message': 'Bill generated successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def export_report(request):
    """Export payment report"""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    try:
        # In a real application, this would generate a CSV or Excel file
        # For now, we'll just return a message
        messages.success(request, 'Report exported successfully')
        return redirect('dashboard:admin_payments')
    except Exception as e:
        messages.error(request, f'Error exporting report: {str(e)}')
        return redirect('dashboard:admin_payments')


@login_required
def download_invoice(request, invoice_id):
    """Download invoice"""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    try:
        # In a real application, this would generate and return a PDF file
        messages.success(request, f'Invoice {invoice_id} downloaded')
        return redirect('dashboard:admin_payments')
    except Exception as e:
        messages.error(request, f'Error downloading invoice: {str(e)}')
        return redirect('dashboard:admin_payments')



@login_required
def admin_appointments(request):
    """Admin appointment management"""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    recent_appointments = Appointment.objects.all().order_by('-created_at')[:10]
    
    context = {
        'recent_appointments': recent_appointments,
    }
    
    return render(request, 'dashboards/admin_appointments.html', context)


@login_required
def admin_payments(request):
    """Admin payment management"""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    payments = Payment.objects.all().order_by('-created_at')
    
    context = {
        'payments': payments,
    }
    
    return render(request, 'dashboards/admin_payments.html', context)


@login_required
def admin_statistics(request):
    """Admin statistics page"""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # Various statistics
    from django.db.models import Count
    from django.db.models.functions import TruncDate
    
    # Appointments by specialty
    appointments_by_specialty = Appointment.objects.values(
        'doctor__specialties__name'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Daily appointments (last 30 days)
    daily_appointments = Appointment.objects.filter(
        created_at__gte=date.today() - timedelta(days=30)
    ).annotate(
        day=TruncDate('created_at')
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')
    
    context = {
        'appointments_by_specialty': appointments_by_specialty,
        'daily_appointments': daily_appointments,
    }
    
    return render(request, 'dashboards/admin_statistics.html', context)


# Employee Dashboard
@login_required
def employee_dashboard(request):
    """Employee dashboard"""
    if not request.user.is_employee():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # Get all appointments (employee manages all appointments)
    all_appointments = Appointment.objects.all().order_by('-created_at')
    
    # Pending appointments
    pending_appointments = Appointment.objects.filter(
        status='pending'
    ).order_by('date', 'time_slot')[:5]
    
    # Today's confirmed appointments
    today_confirmed = Appointment.objects.filter(
        date=date.today(),
        status='confirmed'
    ).count()
    
    # Total pending
    pending_count = Appointment.objects.filter(status='pending').count()
    
    # Statistics for employee
    total_managed = Appointment.objects.exclude(status='pending').count()
    completed_count = Appointment.objects.filter(status='completed').count()
    cancelled_count = Appointment.objects.filter(status='cancelled').count()
    
    # Completion rate calculation
    if total_managed > 0:
        completion_rate = round((completed_count / total_managed) * 100)
    else:
        completion_rate = 0
    
    # Total revenue from managed appointments
    total_revenue = sum(
        appt.total_amount for appt in Appointment.objects.exclude(status='pending')
    )
    
    context = {
        'pending_appointments': pending_appointments,
        'all_appointments': all_appointments,
        'today_confirmed': today_confirmed,
        'pending_count': pending_count,
        'total_managed': total_managed,
        'completed_count': completed_count,
        'cancelled_count': cancelled_count,
        'completion_rate': completion_rate,
        'total_revenue': total_revenue,
    }
    
    return render(request, 'dashboards/employee_dashboard.html', context)


@login_required
def employee_appointments(request):
    """Employee appointment view with search and filter"""
    if not request.user.is_employee():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # Get base queryset
    appointments = Appointment.objects.all().order_by('-created_at')
    
    # Get search query
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '')
    
    # Apply search filter
    if search_query:
        from django.db.models import Q
        appointments = appointments.filter(
            Q(patient__first_name__icontains=search_query) |
            Q(patient__last_name__icontains=search_query) |
            Q(doctor__user__first_name__icontains=search_query) |
            Q(doctor__user__last_name__icontains=search_query)
        )
    
    # Apply status filter
    if status_filter and status_filter != 'all':
        appointments = appointments.filter(status=status_filter)
    
    context = {
        'appointments': appointments,
        'search_query': search_query,
        'status_filter': status_filter,
        'statuses': ['pending', 'confirmed', 'completed', 'cancelled'],
    }
    
    return render(request, 'dashboards/employee_appointments.html', context)


@login_required
def employee_confirm_appointment(request, appointment_id):
    """Employee confirms appointment"""
    if not request.user.is_employee():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    appointment.status = 'confirmed'
    appointment.confirmed_at = timezone.now()
    appointment.save()
    
    # Log history
    from appointments.models import AppointmentHistory
    AppointmentHistory.objects.create(
        appointment=appointment,
        status_from='pending',
        status_to='confirmed',
        changed_by=request.user,
        notes='Confirmed by employee'
    )
    
    messages.success(request, 'Appointment confirmed!')
    return redirect('dashboard:employee_dashboard')
