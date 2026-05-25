"""
Views for appointments app
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from datetime import date, timedelta
import json
from .models import Appointment, CartItem, AppointmentHistory
from doctors.models import Doctor, Hospital, DoctorAvailability
from payments.models import Invoice


def book_appointment(request, doctor_id):
    """Multi-step appointment booking - NO LOGIN REQUIRED"""
    doctor = get_object_or_404(Doctor, pk=doctor_id, is_verified=True, is_active=True)
    step = request.GET.get('step', '1')
    
    # Get next 21 days of availability
    start_date = date.today()
    end_date = start_date + timedelta(days=21)
    
    availabilities = DoctorAvailability.objects.filter(
        doctor=doctor,
        date__gte=start_date,
        date__lte=end_date,
        is_available=True,
        is_booked=False
    ).select_related('hospital').order_by('date', 'time_slot')
    
    hospitals = doctor.hospitals.filter(is_active=True)
    
    # Serialize availabilities for JavaScript
    availabilities_json = json.dumps([
        {
            'id': av.id,
            'date': av.date.isoformat(),
            'time_slot': av.time_slot,
            'hospital_id': av.hospital.id,
            'hospital_name': av.hospital.name,
        }
        for av in availabilities
    ])
    
    context = {
        'doctor': doctor,
        'step': step,
        'availabilities': availabilities,
        'availabilities_json': availabilities_json,
        'hospitals': hospitals,
    }
    
    # Handle form submissions
    if request.method == 'POST':
        step = request.POST.get('step', '1')
        
        if step == '1':
            # Save appointment selection to session
            availability_id = request.POST.get('availability_id')
            hospital_id = request.POST.get('hospital_id')
            consultation_type = request.POST.get('consultation_type', 'in_person')
            
            # Validate selection
            if not availability_id:
                messages.error(request, 'Please select an appointment slot first.')
                return redirect(f'/appointments/book/{doctor_id}/?step=1')
            
            request.session['booking'] = {
                'doctor_id': doctor_id,
                'availability_id': availability_id,
                'hospital_id': hospital_id,
                'consultation_type': consultation_type,
            }
            
            return redirect(f'/appointments/book/{doctor_id}/?step=2')
        
        elif step == '2':
            # Save patient info
            full_name = request.POST.get('full_name')
            age = request.POST.get('age')
            gender = request.POST.get('gender')
            phone = request.POST.get('phone')
            email = request.POST.get('email')
            symptoms = request.POST.get('symptoms')
            
            booking = request.session.get('booking', {})
            booking.update({
                'full_name': full_name,
                'age': age,
                'gender': gender,
                'phone': phone,
                'email': email,
                'symptoms': symptoms,
            })
            request.session['booking'] = booking
            
            return redirect(f'/appointments/book/{doctor_id}/?step=3')
        
        elif step == '3':
            # Save payment method
            payment_method = request.POST.get('payment_method')
            
            booking = request.session.get('booking', {})
            booking['payment_method'] = payment_method
            request.session['booking'] = booking
            
            # If user is logged in, create appointment directly
            if request.user.is_authenticated and request.user.is_patient():
                return redirect(f'/appointments/book/{doctor_id}/?step=5')
            else:
                # For guest users, go to login/signup step
                return redirect(f'/appointments/book/{doctor_id}/?step=4')
        
        elif step == '4':
            # Login/Signup/Guest choice
            auth_choice = request.POST.get('auth_choice')
            booking = request.session.get('booking', {})
            booking['auth_choice'] = auth_choice
            request.session['booking'] = booking
            
            if auth_choice == 'guest':
                return redirect(f'/appointments/book/{doctor_id}/?step=5')
            elif auth_choice == 'login':
                return redirect(f'/accounts/login/?next=/appointments/book/{doctor_id}/?step=5')
            elif auth_choice == 'signup':
                return redirect(f'/accounts/register/?next=/appointments/book/{doctor_id}/?step=5')
        
        elif step == '5':
            # Create appointment
            booking = request.session.get('booking', {})
            
            try:
                availability = DoctorAvailability.objects.get(
                    id=booking.get('availability_id')
                )
                doctor_obj = Doctor.objects.get(pk=doctor_id)
                
                # Handle guest vs registered user
                if request.user.is_authenticated:
                    patient = request.user
                else:
                    # For guest users, we can create a temporary guest record or save to session
                    patient = None
                
                # Create appointment
                if patient:
                    appointment = Appointment.objects.create(
                        patient=patient,
                        doctor=doctor_obj,
                        availability=availability,
                        consultation_type=booking.get('consultation_type'),
                        payment_method=booking.get('payment_method'),
                        status='pending',
                        notes=booking.get('symptoms', ''),
                    )
                else:
                    # For guest users, store in session for confirmation
                    request.session['guest_appointment'] = {
                        'doctor_name': doctor_obj.user.get_full_name(),
                        'full_name': booking.get('full_name'),
                        'email': booking.get('email'),
                        'phone': booking.get('phone'),
                        'availability': str(availability),
                        'payment_method': booking.get('payment_method'),
                    }
                    appointment = None
                
                # Mark availability as booked
                availability.is_booked = True
                availability.save()
                
                # Clear session
                del request.session['booking']
                
                if appointment:
                    messages.success(request, 'Appointment booked successfully!')
                    return redirect('appointments:confirmation', appointment_id=appointment.id)
                else:
                    return redirect(f'/appointments/confirmation-guest/?doctor_id={doctor_id}')
            except Exception as e:
                messages.error(request, f'Error booking appointment: {str(e)}')
                return redirect(f'/appointments/book/{doctor_id}/?step=1')
    
    if step == '2':
        booking = request.session.get('booking', {})
        if not booking.get('availability_id'):
            messages.warning(request, 'Please select an appointment slot first.')
            return redirect(f'/appointments/book/{doctor_id}/?step=1')
        
        availability = DoctorAvailability.objects.get(id=booking.get('availability_id'))
        context['selected_availability'] = availability
        
        # Pre-fill with user data if logged in
        if request.user.is_authenticated:
            context['user_full_name'] = request.user.get_full_name()
            context['user_email'] = request.user.email
            context['user_phone'] = getattr(request.user, 'phone', '')
    
    elif step == '3':
        booking = request.session.get('booking', {})
        if not booking.get('phone'):
            messages.warning(request, 'Please fill in patient information first.')
            return redirect(f'/appointments/book/{doctor_id}/?step=2')
    
    elif step == '4':
        # Login/Signup/Guest choice step
        booking = request.session.get('booking', {})
        if not booking.get('payment_method'):
            messages.warning(request, 'Please select a payment method first.')
            return redirect(f'/appointments/book/{doctor_id}/?step=3')
    
    return render(request, 'appointments/book_appointment.html', context)


@login_required
def confirmation(request, appointment_id):
    """Appointment confirmation page"""
    appointment = get_object_or_404(Appointment, pk=appointment_id, patient=request.user)
    
    context = {
        'appointment': appointment,
    }
    
    return render(request, 'appointments/confirmation.html', context)


def confirmation_guest(request):
    """Guest appointment confirmation page (no login required)"""
    guest_appointment = request.session.get('guest_appointment')
    
    if not guest_appointment:
        messages.error(request, 'No booking information found.')
        return redirect('home')
    
    context = {
        'guest_appointment': guest_appointment,
    }
    
    return render(request, 'appointments/confirmation_guest.html', context)


@login_required
def cart_view(request):
    """View shopping cart"""
    if not request.user.is_patient():
        messages.error(request, 'Only patients can view cart.')
        return redirect('home')
    
    cart_items = CartItem.objects.filter(patient=request.user).select_related(
        'doctor', 'hospital', 'availability'
    )
    
    total = sum(item.get_total() for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'cart_count': cart_items.count(),
    }
    
    return render(request, 'appointments/cart.html', context)


@login_required
def add_to_cart(request, availability_id):
    """Add appointment to cart"""
    if not request.user.is_patient():
        messages.error(request, 'Only patients can add to cart.')
        return redirect('home')
    
    availability = get_object_or_404(
        DoctorAvailability, 
        id=availability_id, 
        is_available=True, 
        is_booked=False
    )
    
    # Get consultation type
    consultation_type = request.POST.get('consultation_type', 'in_person')
    symptoms = request.POST.get('symptoms', '')
    
    # Calculate fees
    if consultation_type == 'online':
        consultation_fee = availability.doctor.consultation_fee_online
    else:
        consultation_fee = availability.doctor.consultation_fee_in_person
    
    # Service fee based on location (simplified)
    service_fee = 50  # Base service fee
    
    # Check if already in cart
    if CartItem.objects.filter(patient=request.user, availability=availability).exists():
        messages.warning(request, 'This slot is already in your cart.')
        return redirect('doctors:detail', pk=availability.doctor.id)
    
    # Create cart item
    CartItem.objects.create(
        patient=request.user,
        doctor=availability.doctor,
        hospital=availability.hospital,
        availability=availability,
        consultation_type=consultation_type,
        symptoms=symptoms,
        consultation_fee=consultation_fee,
        service_fee=service_fee
    )
    
    messages.success(request, 'Added to cart successfully!')
    return redirect('appointments:cart')


@login_required
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    if not request.user.is_patient():
        messages.error(request, 'Only patients can manage cart.')
        return redirect('home')
    
    cart_item = get_object_or_404(CartItem, id=item_id, patient=request.user)
    cart_item.delete()
    
    messages.success(request, 'Item removed from cart.')
    return redirect('appointments:cart')


@login_required
def clear_cart(request):
    """Clear all items from cart"""
    if not request.user.is_patient():
        messages.error(request, 'Only patients can manage cart.')
        return redirect('home')
    
    CartItem.objects.filter(patient=request.user).delete()
    messages.success(request, 'Cart cleared.')
    return redirect('appointments:cart')


@login_required

@login_required
def checkout(request):
    """Checkout cart items"""
    if not request.user.is_patient():
        messages.error(request, 'Only patients can checkout.')
        return redirect('home')
    
    cart_items = CartItem.objects.filter(patient=request.user)
    
    if not cart_items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('appointments:cart')
    
    if request.method == 'POST':
        appointments = []
        
        with transaction.atomic():
            for item in cart_items:
                # Create appointment
                appointment = Appointment.objects.create(
                    patient=request.user,
                    doctor=item.doctor,
                    hospital=item.hospital,
                    date=item.availability.date,
                    time_slot=item.availability.time_slot,
                    consultation_type=item.consultation_type,
                    symptoms=item.symptoms,
                    consultation_fee=item.consultation_fee,
                    service_fee=item.service_fee
                )
                
                # Mark availability as booked
                item.availability.is_booked = True
                item.availability.save()
                
                appointments.append(appointment)
            
            # Clear cart
            cart_items.delete()
        
        if len(appointments) == 1:
            return redirect('payments:process', appointment_id=appointments[0].id)
        else:
            messages.success(request, f'{len(appointments)} appointments booked!')
            return redirect('appointments:my_appointments')
    
    total = sum(item.get_total() for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total': total,
    }
    
    return render(request, 'appointments/checkout.html', context)


@login_required
def confirm_appointment(request, appointment_id):
    """Confirm appointment (for admin/employee)"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if not (request.user.is_super_admin() or request.user.is_employee()):
        messages.error(request, 'You do not have permission to confirm appointments.')
        return redirect('home')
    
    appointment.status = 'confirmed'
    appointment.confirmed_at = timezone.now()
    appointment.save()
    
    # Log history
    AppointmentHistory.objects.create(
        appointment=appointment,
        status_from='pending',
        status_to='confirmed',
        changed_by=request.user,
        notes='Confirmed by staff'
    )
    
    messages.success(request, 'Appointment confirmed!')
    return redirect('dashboard:employee_dashboard')


@login_required
def my_appointments(request):
    """View patient's appointments"""
    if not request.user.is_patient():
        messages.error(request, 'Only patients can view appointments.')
        return redirect('home')
    
    # Upcoming appointments
    upcoming = Appointment.objects.filter(
        patient=request.user,
        date__gte=date.today(),
        status__in=['pending', 'confirmed']
    ).order_by('date', 'time_slot')
    
    # Past appointments
    past = Appointment.objects.filter(
        patient=request.user
    ).exclude(
        date__gte=date.today(),
        status__in=['pending', 'confirmed']
    ).order_by('-date', '-time_slot')[:10]
    
    context = {
        'upcoming_appointments': upcoming,
        'past_appointments': past,
    }
    
    return render(request, 'appointments/my_appointments.html', context)


@login_required
def appointment_detail(request, appointment_id):
    """View appointment details"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check permission
    if not (request.user == appointment.patient or 
            request.user == appointment.doctor.user or
            request.user.is_super_admin() or
            request.user.is_employee()):
        messages.error(request, 'You do not have permission to view this appointment.')
        return redirect('home')
    
    # Get invoice if exists
    try:
        invoice = appointment.invoice
    except:
        invoice = None
    
    context = {
        'appointment': appointment,
        'invoice': invoice,
    }
    
    return render(request, 'appointments/appointment_detail.html', context)


@login_required
def cancel_appointment(request, appointment_id):
    """Cancel appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check permission
    if not (request.user == appointment.patient or 
            request.user == appointment.doctor.user or
            request.user.is_super_admin()):
        messages.error(request, 'You do not have permission to cancel this appointment.')
        return redirect('home')
    
    if appointment.status in ['completed', 'cancelled']:
        messages.error(request, 'Cannot cancel this appointment.')
        return redirect('appointments:detail', appointment_id=appointment_id)
    
    old_status = appointment.status
    appointment.status = 'cancelled'
    appointment.cancelled_at = timezone.now()
    appointment.save()
    
    # Free up availability
    try:
        availability = DoctorAvailability.objects.get(
            doctor=appointment.doctor,
            hospital=appointment.hospital,
            date=appointment.date,
            time_slot=appointment.time_slot
        )
        availability.is_booked = False
        availability.save()
    except DoctorAvailability.DoesNotExist:
        pass
    
    # Log history
    AppointmentHistory.objects.create(
        appointment=appointment,
        status_from=old_status,
        status_to='cancelled',
        changed_by=request.user,
        notes='Cancelled by user'
    )
    
    messages.success(request, 'Appointment cancelled.')
    return redirect('appointments:my_appointments')


@login_required
def reschedule_appointment(request, appointment_id):
    """Reschedule appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    
    if appointment.status in ['completed', 'cancelled']:
        messages.error(request, 'Cannot reschedule this appointment.')
        return redirect('appointments:detail', appointment_id=appointment_id)
    
    # Get available slots for next 7 days
    availabilities = DoctorAvailability.objects.filter(
        doctor=appointment.doctor,
        date__gte=date.today(),
        date__lte=date.today() + timedelta(days=7),
        is_available=True,
        is_booked=False
    ).order_by('date', 'time_slot')
    
    if request.method == 'POST':
        availability_id = request.POST.get('availability_id')
        new_availability = get_object_or_404(DoctorAvailability, id=availability_id)
        
        # Free up old availability
        try:
            old_availability = DoctorAvailability.objects.get(
                doctor=appointment.doctor,
                hospital=appointment.hospital,
                date=appointment.date,
                time_slot=appointment.time_slot
            )
            old_availability.is_booked = False
            old_availability.save()
        except DoctorAvailability.DoesNotExist:
            pass
        
        # Update appointment
        old_date = appointment.date
        old_time = appointment.time_slot
        appointment.date = new_availability.date
        appointment.time_slot = new_availability.time_slot
        appointment.hospital = new_availability.hospital
        appointment.save()
        
        # Mark new availability as booked
        new_availability.is_booked = True
        new_availability.save()
        
        # Log history
        AppointmentHistory.objects.create(
            appointment=appointment,
            status_from=appointment.status,
            status_to=appointment.status,
            changed_by=request.user,
            notes=f'Rescheduled from {old_date} {old_time} to {appointment.date} {appointment.time_slot}'
        )
        
        messages.success(request, 'Appointment rescheduled!')
        return redirect('appointments:detail', appointment_id=appointment_id)
    
    context = {
        'appointment': appointment,
        'availabilities': availabilities,
    }
    
    return render(request, 'appointments/reschedule.html', context)


# Doctor views
@login_required
def doctor_appointments(request):
    """View doctor's appointments"""
    if not request.user.is_doctor():
        messages.error(request, 'Only doctors can view this page.')
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
    upcoming = Appointment.objects.filter(
        doctor=doctor,
        date__gt=date.today(),
        status__in=['pending', 'confirmed']
    ).order_by('date', 'time_slot')
    
    # Past appointments
    past = Appointment.objects.filter(
        doctor=doctor
    ).exclude(
        date__gte=date.today(),
        status__in=['pending', 'confirmed']
    ).order_by('-date', '-time_slot')[:10]

    # Get hospitals associated with the doctor
    from doctors.models import DoctorHospital
    doctor_hospitals = DoctorHospital.objects.filter(doctor=doctor).select_related('hospital')
    hospitals = [dh.hospital for dh in doctor_hospitals]
    
    context = {
        'doctor': doctor,
        'today_appointments': today_appointments,
        'upcoming_appointments': upcoming,
        'past_appointments': past,
        'hospitals': hospitals,
    }
    
    return render(request, 'appointments/doctor_appointments.html', context)


@login_required
def doctor_confirm(request, appointment_id):
    """Doctor confirms appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if request.user != appointment.doctor.user:
        messages.error(request, 'You can only confirm your own appointments.')
        return redirect('home')
    
    old_status = appointment.status
    appointment.status = 'confirmed'
    appointment.confirmed_at = timezone.now()
    appointment.save()
    
    # Log history
    AppointmentHistory.objects.create(
        appointment=appointment,
        status_from=old_status,
        status_to='confirmed',
        changed_by=request.user,
        notes='Confirmed by doctor'
    )
    
    messages.success(request, 'Appointment confirmed!')
    return redirect('appointments:doctor_appointments')


@login_required
def doctor_complete(request, appointment_id):
    """Doctor marks appointment as completed"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if request.user != appointment.doctor.user:
        messages.error(request, 'You can only complete your own appointments.')
        return redirect('home')
    
    old_status = appointment.status
    appointment.status = 'completed'
    appointment.completed_at = timezone.now()
    appointment.save()
    
    # Log history
    AppointmentHistory.objects.create(
        appointment=appointment,
        status_from=old_status,
        status_to='completed',
        changed_by=request.user,
        notes='Completed by doctor'
    )
    
    messages.success(request, 'Appointment marked as completed!')
    return redirect('appointments:doctor_appointments')


@login_required
def add_prescription(request, appointment_id):
    """Doctor adds prescription"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if request.user != appointment.doctor.user:
        messages.error(request, 'You can only add prescriptions to your own appointments.')
        return redirect('home')
    
    if request.method == 'POST':
        prescription = request.POST.get('prescription', '')
        prescription_file = request.FILES.get('prescription_file')
        
        appointment.prescription = prescription
        if prescription_file:
            appointment.prescription_file = prescription_file
        appointment.save()
        
        messages.success(request, 'Prescription added!')
        return redirect('appointments:doctor_appointments')
    
    context = {
        'appointment': appointment,
    }
    
    return render(request, 'appointments/add_prescription.html', context)


# API views
def check_availability(request):
    """AJAX endpoint to check availability"""
    doctor_id = request.GET.get('doctor_id')
    date_str = request.GET.get('date')
    
    if not doctor_id or not date_str:
        return JsonResponse({'error': 'Missing parameters'}, status=400)
    
    try:
        from datetime import datetime
        check_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        availabilities = DoctorAvailability.objects.filter(
            doctor_id=doctor_id,
            date=check_date,
            is_available=True,
            is_booked=False
        ).values('id', 'time_slot', 'hospital__name')
        
        return JsonResponse({
            'availabilities': list(availabilities)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
