"""
Views for payments app
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db import transaction
from datetime import datetime
import uuid

from .models import Payment, Invoice, DoctorEarning
from appointments.models import Appointment


@login_required
def process_payment(request, appointment_id):
    """Process payment for appointment"""
    appointment = get_object_or_404(
        Appointment, 
        id=appointment_id, 
        patient=request.user,
        is_paid=False
    )
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        
        if not payment_method:
            messages.error(request, 'Please select a payment method.')
            return redirect('payments:process', appointment_id=appointment_id)
        
        # Create payment record
        payment = Payment.objects.create(
            appointment=appointment,
            amount=appointment.total_amount,
            method=payment_method
        )
        
        # Generate transaction ID
        payment.generate_transaction_id()
        
        # For cash on arrival, mark as pending
        if payment_method == 'cash':
            payment.status = 'pending'
            payment.save()
            
            # Create invoice
            invoice = Invoice.objects.create(
                appointment=appointment,
                consultation_fee=appointment.consultation_fee,
                service_fee=appointment.service_fee,
                total_amount=appointment.total_amount,
                payment_method=payment_method
            )
            invoice.generate_invoice_number()
            invoice.save()
            
            messages.success(request, 'Appointment booked! Please pay cash at the hospital.')
            return redirect('payments:view_invoice', invoice_id=invoice.id)
        
        # For digital payments, simulate processing
        payment.status = 'processing'
        payment.save()
        
        # Simulate payment gateway processing
        # In production, integrate with actual payment gateway
        
        # Simulate successful payment
        payment.status = 'completed'
        payment.completed_at = timezone.now()
        payment.save()
        
        # Update appointment
        appointment.is_paid = True
        appointment.payment_method = payment_method
        appointment.save()
        
        # Create invoice
        invoice = Invoice.objects.create(
            appointment=appointment,
            consultation_fee=appointment.consultation_fee,
            service_fee=appointment.service_fee,
            total_amount=appointment.total_amount,
            payment_method=payment_method,
            transaction_id=payment.transaction_id,
            paid_at=timezone.now()
        )
        invoice.generate_invoice_number()
        invoice.save()
        
        # Create doctor earning record
        doctor_earning = DoctorEarning.objects.create(
            doctor=appointment.doctor,
            appointment=appointment,
            total_amount=appointment.consultation_fee,
            commission_rate=appointment.doctor.commission_rate,
            month=timezone.now().month,
            year=timezone.now().year
        )
        doctor_earning.calculate_earnings()
        doctor_earning.save()
        
        messages.success(request, 'Payment successful!')
        return redirect('payments:success', payment_id=payment.id)
    
    context = {
        'appointment': appointment,
    }
    
    return render(request, 'payments/process_payment.html', context)


@login_required
def payment_success(request, payment_id):
    """Payment success page"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    # Check permission
    if request.user != payment.appointment.patient and not request.user.is_super_admin():
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('home')
    
    try:
        invoice = payment.appointment.invoice
    except:
        invoice = None
    
    context = {
        'payment': payment,
        'invoice': invoice,
    }
    
    return render(request, 'payments/payment_success.html', context)


@login_required
def payment_failed(request, payment_id):
    """Payment failed page"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    context = {
        'payment': payment,
    }
    
    return render(request, 'payments/payment_failed.html', context)


@login_required
def payment_history(request):
    """View payment history"""
    if request.user.is_patient():
        payments = Payment.objects.filter(
            appointment__patient=request.user,
            status='completed'
        ).order_by('-created_at')
    elif request.user.is_doctor():
        payments = Payment.objects.filter(
            appointment__doctor=request.user.doctor_profile,
            status='completed'
        ).order_by('-created_at')
    else:
        payments = Payment.objects.none()
    
    context = {
        'payments': payments,
    }
    
    return render(request, 'payments/payment_history.html', context)


@login_required
def view_invoice(request, invoice_id):
    """View invoice"""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    # Check permission
    if not (request.user == invoice.appointment.patient or 
            request.user == invoice.appointment.doctor.user or
            request.user.is_super_admin() or
            request.user.is_employee()):
        messages.error(request, 'You do not have permission to view this invoice.')
        return redirect('home')
    
    context = {
        'invoice': invoice,
        'appointment': invoice.appointment,
    }
    
    return render(request, 'payments/view_invoice.html', context)


@login_required
def download_invoice(request, invoice_id):
    """Download invoice as PDF"""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    # Check permission
    if not (request.user == invoice.appointment.patient or 
            request.user == invoice.appointment.doctor.user or
            request.user.is_super_admin()):
        messages.error(request, 'You do not have permission to download this invoice.')
        return redirect('home')
    
    # For now, return HTML as text (in production, generate PDF)
    html_content = f"""
    INVOICE
    =======
    Invoice Number: {invoice.invoice_number}
    Date: {invoice.created_at.strftime('%Y-%m-%d')}
    
    Patient: {invoice.appointment.patient.get_full_name()}
    Doctor: {invoice.appointment.doctor.get_full_name()}
    
    Consultation Fee: ৳{invoice.consultation_fee}
    Service Fee: ৳{invoice.service_fee}
    Total: ৳{invoice.total_amount}
    
    Payment Method: {invoice.get_payment_method_display()}
    Transaction ID: {invoice.transaction_id}
    """
    
    response = HttpResponse(html_content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.txt"'
    return response


@login_required
def doctor_earnings(request):
    """View doctor earnings"""
    if not request.user.is_doctor():
        messages.error(request, 'Only doctors can view earnings.')
        return redirect('home')
    
    try:
        doctor = request.user.doctor_profile
    except:
        messages.error(request, 'Doctor profile not found.')
        return redirect('home')
    
    # Get earnings
    earnings = DoctorEarning.objects.filter(doctor=doctor).order_by('-created_at')
    
    # Calculate totals
    total_earned = sum(e.doctor_amount for e in earnings if e.is_paid_to_doctor)
    pending_earnings = sum(e.doctor_amount for e in earnings if not e.is_paid_to_doctor)
    total_amount = total_earned + pending_earnings
    avg_per_transaction = round(total_amount / len(earnings), 2) if earnings else 0
    
    # Monthly breakdown
    from django.db.models import Sum
    monthly_earnings = DoctorEarning.objects.filter(
        doctor=doctor,
        is_paid_to_doctor=True
    ).values('year', 'month').annotate(
        total=Sum('doctor_amount')
    ).order_by('-year', '-month')[:12]
    
    context = {
        'doctor': doctor,
        'earnings': earnings,
        'total_earned': total_earned,
        'pending_earnings': pending_earnings,
        'avg_per_transaction': avg_per_transaction,
        'monthly_earnings': monthly_earnings,
    }
    
    return render(request, 'payments/doctor_earnings.html', context)


@login_required
def request_refund(request, payment_id):
    """Request refund"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    # Check permission
    if request.user != payment.appointment.patient:
        messages.error(request, 'You can only request refunds for your own payments.')
        return redirect('home')
    
    # Check if eligible for refund
    if payment.status != 'completed':
        messages.error(request, 'This payment is not eligible for refund.')
        return redirect('payments:history')
    
    # Check if already refunded
    if hasattr(payment, 'refunds') and payment.refunds.filter(status__in=['pending', 'approved']).exists():
        messages.error(request, 'A refund request is already pending for this payment.')
        return redirect('payments:history')
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        
        from .models import Refund
        refund = Refund.objects.create(
            payment=payment,
            amount=payment.amount,
            reason=reason
        )
        
        messages.success(request, 'Refund request submitted. We will review it shortly.')
        return redirect('payments:history')
    
    context = {
        'payment': payment,
    }
    
    return render(request, 'payments/request_refund.html', context)
