"""
Management command to create demo data for testing
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from doctors.models import Doctor, Specialty, Hospital, DoctorAvailability, DoctorHospital, Review
from accounts.models import PatientProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Create demo data for testing the healthcare platform'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating demo data...'))
        
        # Create demo hospitals
        hospitals = self.create_hospitals()
        
        # Create demo doctors
        doctors = self.create_doctors(hospitals)
        
        # Create demo availability
        self.create_availability(doctors, hospitals)
        
        # Create demo patient
        patient = self.create_patient()
        
        # Create demo employees
        self.create_employees()
        
        # Create demo reviews
        self.create_reviews(doctors)
        
        # Create demo appointments
        self.create_appointments(patient, doctors, hospitals)
        
        # Create demo payments
        self.create_payments()
        
        self.stdout.write(self.style.SUCCESS('\n✓ All demo data created successfully!'))
        self.stdout.write(self.style.WARNING('\nTest Credentials:'))
        self.stdout.write(self.style.WARNING('  Admin: Shourov / Shourov'))
        self.stdout.write(self.style.WARNING('  Patient: patient@drseba.com / demo123456'))
        self.stdout.write(self.style.WARNING('  Doctor: dr.karim@drseba.com / demo123456'))
        self.stdout.write(self.style.WARNING('  Employee: employee@drseba.com / demo123456'))
    
    def create_hospitals(self):
        """Create demo hospitals"""
        hospitals_data = [
            {
                'name': 'Dhaka Medical College',
                'address': '123 Medical Plaza, Dhanmondi',
                'city': 'Dhaka',
                'district': 'Dhaka',
                'phone': '+8809678901',
                'email': 'info@dmc.gov.bd',
                'total_beds': 150,
                'icu_beds_available': 12,
            },
            {
                'name': 'Bangabandhu Sheikh Mujib Medical University',
                'address': '456 Health Avenue, Gulshan',
                'city': 'Dhaka',
                'district': 'Dhaka',
                'phone': '+8809678902',
                'email': 'info@bsmmu.edu.bd',
                'total_beds': 200,
                'icu_beds_available': 8,
            },
            {
                'name': 'Sir Salimullah Medical College',
                'address': '789 Care Street, Panthapath',
                'city': 'Dhaka',
                'district': 'Dhaka',
                'phone': '+8809678903',
                'email': 'info@smc.gov.bd',
                'total_beds': 120,
                'icu_beds_available': 15,
            },
            {
                'name': 'Chittagong Medical College',
                'address': '321 Hospital Road, Chittagong',
                'city': 'Chittagong',
                'district': 'Chittagong',
                'phone': '+8809678904',
                'email': 'info@cmc.gov.bd',
                'total_beds': 180,
                'icu_beds_available': 10,
            },
        ]
        
        hospitals = []
        for hospital_data in hospitals_data:
            hospital, created = Hospital.objects.get_or_create(
                name=hospital_data['name'],
                defaults=hospital_data
            )
            if created:
                self.stdout.write(f'  ✓ Created hospital: {hospital.name}')
            hospitals.append(hospital)
        
        return hospitals
    
    def create_doctors(self, hospitals):
        """Create demo doctors"""
        doctors_data = [
            {
                'first_name': 'Karim',
                'last_name': 'Ahmed',
                'email': 'dr.karim@drseba.com',
                'phone': '+8801711111111',
                'role': 'doctor',
                'doctor': {
                    'bmdc_number': 'BMDC001',
                    'qualifications': 'MBBS, MD (Cardiology)',
                    'experience_years': 12,
                    'about': 'Experienced cardiologist with expertise in complex cardiac cases',
                    'consultation_fee_online': Decimal('500.00'),
                    'consultation_fee_in_person': Decimal('1000.00'),
                    'is_verified': True,
                    'rating': Decimal('4.8'),
                    'total_reviews': 45,
                    'specialties': ['Cardiologist'],
                }
            },
            {
                'first_name': 'Fatima',
                'last_name': 'Khan',
                'email': 'dr.fatima@drseba.com',
                'phone': '+8801722222222',
                'role': 'doctor',
                'doctor': {
                    'bmdc_number': 'BMDC002',
                    'qualifications': 'MBBS, BCS (Pediatrics)',
                    'experience_years': 8,
                    'about': 'Specialized in child health and development',
                    'consultation_fee_online': Decimal('400.00'),
                    'consultation_fee_in_person': Decimal('800.00'),
                    'is_verified': True,
                    'rating': Decimal('4.9'),
                    'total_reviews': 52,
                    'specialties': ['Pediatrician'],
                }
            },
            {
                'first_name': 'Mohammad',
                'last_name': 'Hasan',
                'email': 'dr.hasan@drseba.com',
                'phone': '+8801733333333',
                'role': 'doctor',
                'doctor': {
                    'bmdc_number': 'BMDC003',
                    'qualifications': 'MBBS, DO (Ophthalmology)',
                    'experience_years': 10,
                    'about': 'Expert in eye care and vision correction',
                    'consultation_fee_online': Decimal('450.00'),
                    'consultation_fee_in_person': Decimal('900.00'),
                    'is_verified': True,
                    'rating': Decimal('4.7'),
                    'total_reviews': 38,
                    'specialties': ['Ophthalmologist'],
                }
            },
            {
                'first_name': 'Ayesha',
                'last_name': 'Begum',
                'email': 'dr.ayesha@drseba.com',
                'phone': '+8801744444444',
                'role': 'doctor',
                'doctor': {
                    'bmdc_number': 'BMDC004',
                    'qualifications': 'MBBS, MS (Orthopedics)',
                    'experience_years': 11,
                    'about': 'Specialist in bone and joint disorders',
                    'consultation_fee_online': Decimal('550.00'),
                    'consultation_fee_in_person': Decimal('1100.00'),
                    'is_verified': True,
                    'rating': Decimal('4.6'),
                    'total_reviews': 41,
                    'specialties': ['Orthopedic'],
                }
            },
            {
                'first_name': 'Sohel',
                'last_name': 'Rahman',
                'email': 'dr.sohel@drseba.com',
                'phone': '+8801755555555',
                'role': 'doctor',
                'doctor': {
                    'bmdc_number': 'BMDC005',
                    'qualifications': 'MBBS, Diploma in Neurology',
                    'experience_years': 9,
                    'about': 'Experienced neurologist with expertise in headaches and seizures',
                    'consultation_fee_online': Decimal('600.00'),
                    'consultation_fee_in_person': Decimal('1200.00'),
                    'is_verified': True,
                    'rating': Decimal('4.8'),
                    'total_reviews': 36,
                    'specialties': ['Neurologist'],
                }
            },
            {
                'first_name': 'Nasrin',
                'last_name': 'Akter',
                'email': 'dr.nasrin@drseba.com',
                'phone': '+8801766666666',
                'role': 'doctor',
                'doctor': {
                    'bmdc_number': 'BMDC006',
                    'qualifications': 'MBBS, MD (Dermatology)',
                    'experience_years': 7,
                    'about': 'Skin specialist with expertise in cosmetic and medical dermatology',
                    'consultation_fee_online': Decimal('400.00'),
                    'consultation_fee_in_person': Decimal('800.00'),
                    'is_verified': True,
                    'rating': Decimal('4.9'),
                    'total_reviews': 48,
                    'specialties': ['Dermatologist'],
                }
            },
            {
                'first_name': 'Rafiq',
                'last_name': 'Uddin',
                'email': 'dr.rafiq@drseba.com',
                'phone': '+8801777777777',
                'role': 'doctor',
                'doctor': {
                    'bmdc_number': 'BMDC007',
                    'qualifications': 'MBBS, MD (Internal Medicine)',
                    'experience_years': 13,
                    'about': 'General physician with expertise in chronic diseases',
                    'consultation_fee_online': Decimal('350.00'),
                    'consultation_fee_in_person': Decimal('700.00'),
                    'is_verified': True,
                    'rating': Decimal('4.5'),
                    'total_reviews': 55,
                    'specialties': ['Medicine Specialist'],
                }
            },
            {
                'first_name': 'Nasima',
                'last_name': 'Sultana',
                'email': 'dr.nasima@drseba.com',
                'phone': '+8801788888888',
                'role': 'doctor',
                'doctor': {
                    'bmdc_number': 'BMDC008',
                    'qualifications': 'MBBS, DGO (Obstetrics & Gynecology)',
                    'experience_years': 11,
                    'about': 'Experienced gynecologist with expertise in women health',
                    'consultation_fee_online': Decimal('500.00'),
                    'consultation_fee_in_person': Decimal('1000.00'),
                    'is_verified': True,
                    'rating': Decimal('4.7'),
                    'total_reviews': 43,
                    'specialties': ['Gynecologist'],
                }
            },
        ]
        
        doctors = []
        specialties = Specialty.objects.all()
        
        for doc_data in doctors_data:
            # Create or get user
            user, created = User.objects.get_or_create(
                email=doc_data['email'],
                defaults={
                    'first_name': doc_data['first_name'],
                    'last_name': doc_data['last_name'],
                    'username': doc_data['email'].split('@')[0],
                    'phone': doc_data['phone'],
                    'role': 'doctor',
                    'is_verified': True,
                }
            )
            
            if created:
                user.set_password('demo123456')
                user.save()
            
            # Create or get doctor profile
            doctor_info = doc_data['doctor'].copy()
            specialty_names = doctor_info.pop('specialties')
            
            doctor, created = Doctor.objects.get_or_create(
                user=user,
                defaults=doctor_info
            )
            
            if created:
                # Assign specialties
                for spec_name in specialty_names:
                    spec = specialties.filter(name=spec_name).first()
                    if spec:
                        doctor.specialties.add(spec)
                
                # Assign hospitals using DoctorHospital model
                for idx, hospital in enumerate(hospitals[:2]):
                    DoctorHospital.objects.get_or_create(
                        doctor=doctor,
                        hospital=hospital,
                        defaults={
                            'is_primary': idx == 0,
                            'is_active': True,
                        }
                    )
                
                self.stdout.write(f'  ✓ Created doctor: Dr. {user.get_full_name()}')
            
            doctors.append(doctor)
        
        return doctors
    
    def create_availability(self, doctors, hospitals):
        """Create demo availability slots"""
        slot_times = ['09:00-11:00', '11:00-13:00', '14:00-16:00', '16:00-18:00']
        
        # Create availability for next 14 days
        count = 0
        for doctor in doctors:
            for hospital in hospitals[:2]:
                for days_ahead in range(1, 15):
                    appointment_date = date.today() + timedelta(days=days_ahead)
                    
                    for slot_time in slot_times:
                        availability, created = DoctorAvailability.objects.get_or_create(
                            doctor=doctor,
                            hospital=hospital,
                            date=appointment_date,
                            time_slot=slot_time,
                            defaults={
                                'is_available': True,
                                'is_booked': False,
                            }
                        )
                        if created:
                            count += 1
        
        self.stdout.write(f'  ✓ Created {count} availability slots')
    
    def create_patient(self):
        """Create demo patient account"""
        patient_user, created = User.objects.get_or_create(
            email='patient@drseba.com',
            defaults={
                'first_name': 'Tariq',
                'last_name': 'Hussain',
                'username': 'patient',
                'phone': '+8801900000000',
                'role': 'patient',
                'is_verified': True,
            }
        )
        
        if created:
            patient_user.set_password('demo123456')
            patient_user.save()
            
            # Create patient profile
            PatientProfile.objects.get_or_create(
                user=patient_user,
                defaults={
                    'date_of_birth': date(1990, 5, 15),
                    'gender': 'male',
                    'blood_group': 'O+',
                    'address': '123 Residential Road, Dhaka',
                    'city': 'Dhaka',
                    'district': 'Dhaka',
                    'emergency_contact': '+8801900000001',
                    'medical_history': 'No major medical history',
                    'allergies': 'None known',
                }
            )
            
            self.stdout.write(f'  ✓ Created patient: {patient_user.get_full_name()}')
        
        return patient_user
    
    def create_reviews(self, doctors):
        """Create demo reviews"""
        review_comments = [
            'Excellent doctor with great bedside manner. Highly recommended!',
            'Very professional and knowledgeable. Great experience.',
            'Best doctor I have ever visited. Solved my problem completely.',
            'Good doctor, a bit busy but very competent.',
            'Fantastic service and very caring approach.',
            'Thoroughly checked and explained everything clearly.',
            'Very punctual and dedicated to patient care.',
            'Amazing experience, will visit again!',
        ]
        
        review_ratings = [5, 4, 5, 4, 5, 5, 4, 5]
        
        # Get or create patient
        patient_user = User.objects.filter(email='patient@drseba.com').first()
        
        if patient_user:
            count = 0
            for idx, doctor in enumerate(doctors):
                review, created = Review.objects.get_or_create(
                    doctor=doctor,
                    patient=patient_user,
                    defaults={
                        'rating': review_ratings[idx % len(review_ratings)],
                        'comment': review_comments[idx % len(review_comments)],
                        'is_active': True,
                    }
                )
                if created:
                    count += 1
            
            self.stdout.write(f'  ✓ Created {count} reviews')
    
    def create_employees(self):
        """Create demo employees"""
        employees_data = [
            {
                'first_name': 'Rahima',
                'last_name': 'Akter',
                'email': 'rahima@drseba.com',
                'phone': '+8801712345678',
                'position': 'Appointment Manager',
            },
            {
                'first_name': 'Kamrul',
                'last_name': 'Hasan',
                'email': 'kamrul@drseba.com',
                'phone': '+8801712345679',
                'position': 'Senior Coordinator',
            },
            {
                'first_name': 'Shahinur',
                'last_name': 'Rahman',
                'email': 'shahinur@drseba.com',
                'phone': '+8801712345680',
                'position': 'Appointment Coordinator',
            },
            {
                'first_name': 'Fatima',
                'last_name': 'Khanom',
                'email': 'fatima@drseba.com',
                'phone': '+8801712345681',
                'position': 'Appointment Assistant',
            },
            {
                'first_name': 'Tanvir',
                'last_name': 'Islam',
                'email': 'tanvir@drseba.com',
                'phone': '+8801712345682',
                'position': 'Junior Coordinator',
            },
        ]
        
        count = 0
        for emp_data in employees_data:
            user, created = User.objects.get_or_create(
                email=emp_data['email'],
                defaults={
                    'first_name': emp_data['first_name'],
                    'last_name': emp_data['last_name'],
                    'username': emp_data['email'].split('@')[0],
                    'phone': emp_data['phone'],
                    'role': 'employee',
                    'is_verified': True,
                }
            )
            
            if created:
                user.set_password('demo123456')
                user.save()
                count += 1
        
        self.stdout.write(f'  ✓ Created {count} employees')
    
    def create_appointments(self, patient, doctors, hospitals):
        """Create demo appointments with comprehensive coverage"""
        from appointments.models import Appointment
        
        count = 0
        
        # 1. Create TODAY's appointments for each doctor (for "Today's Appointments" section)
        for idx, doctor in enumerate(doctors[:3]):  # Create for first 3 doctors
            hospital = hospitals[idx % len(hospitals)]
            
            appointment, created = Appointment.objects.get_or_create(
                patient=patient,
                doctor=doctor,
                hospital=hospital,
                date=date.today(),
                time_slot=f'{9 + idx}:00-{10 + idx}:00',
                defaults={
                    'consultation_type': 'in_person',
                    'status': 'confirmed',
                    'consultation_fee': Decimal('800'),
                    'service_fee': Decimal('150'),
                    'total_amount': Decimal('950'),
                    'is_paid': True,
                    'payment_method': 'card',
                    'symptoms': 'General checkup and health consultation',
                }
            )
            if created:
                count += 1
        
        # 2. Create UPCOMING appointments for next 7 days (for "Upcoming" section)
        for idx, doctor in enumerate(doctors):
            hospital = hospitals[idx % len(hospitals)]
            appointment_date = date.today() + timedelta(days=(idx % 7 + 1))
            
            appointment, created = Appointment.objects.get_or_create(
                patient=patient,
                doctor=doctor,
                hospital=hospital,
                date=appointment_date,
                time_slot=f'{10 + (idx % 6)}:00-{11 + (idx % 6)}:00',
                defaults={
                    'consultation_type': 'in_person' if idx % 2 == 0 else 'online',
                    'status': 'pending' if idx % 3 == 0 else 'confirmed',
                    'consultation_fee': Decimal('800'),
                    'service_fee': Decimal('150'),
                    'total_amount': Decimal('950'),
                    'is_paid': True,
                    'payment_method': 'card',
                    'symptoms': 'Follow-up consultation' if idx % 2 else 'New patient evaluation',
                }
            )
            if created:
                count += 1
        
        # 3. Create PAST/COMPLETED appointments (for "Total Patients" and earnings)
        for idx, doctor in enumerate(doctors):
            hospital = hospitals[idx % len(hospitals)]
            # Create appointments from past 30 days
            past_date = date.today() - timedelta(days=(idx % 30 + 1))
            
            appointment, created = Appointment.objects.get_or_create(
                patient=patient,
                doctor=doctor,
                hospital=hospital,
                date=past_date,
                time_slot=f'{14 + (idx % 4)}:00-{15 + (idx % 4)}:00',
                defaults={
                    'consultation_type': 'in_person',
                    'status': 'completed',
                    'consultation_fee': Decimal('800'),
                    'service_fee': Decimal('150'),
                    'total_amount': Decimal('950'),
                    'is_paid': True,
                    'payment_method': 'card',
                    'doctor_notes': 'Follow-up recommended',
                    'symptoms': 'Health consultation',
                }
            )
            if created:
                count += 1
        
        self.stdout.write(f'  ✓ Created {count} appointments')
    
    def create_payments(self):
        """Create demo payments and doctor earnings"""
        from payments.models import Payment, DoctorEarning
        from appointments.models import Appointment
        
        # Create payments for all paid appointments
        appointments = Appointment.objects.filter(is_paid=True)
        
        payment_count = 0
        earning_count = 0
        
        for appt in appointments:
            # Create payment record
            payment, created = Payment.objects.get_or_create(
                appointment=appt,
                defaults={
                    'amount': appt.total_amount,
                    'status': 'completed' if appt.status in ['completed', 'confirmed'] else 'pending',
                    'method': appt.payment_method or 'card',
                    'transaction_id': f'TXN{appt.id}{appt.patient.id}',
                }
            )
            
            if created:
                payment_count += 1
            
            # Create earning record for each completed or confirmed appointment
            if appt.status in ['completed', 'confirmed']:
                earning_exists = DoctorEarning.objects.filter(
                    doctor=appt.doctor,
                    appointment=appt
                ).exists()
                
                if not earning_exists:
                    # Calculate earnings properly
                    total = appt.total_amount
                    commission_rate = Decimal('15.00')
                    platform_commission = (total * commission_rate) / Decimal('100')
                    doctor_amount = total - platform_commission
                    
                    earning = DoctorEarning.objects.create(
                        doctor=appt.doctor,
                        appointment=appt,
                        total_amount=total,
                        commission_rate=commission_rate,
                        platform_commission=platform_commission,
                        doctor_amount=doctor_amount,
                        month=appt.date.month,
                        year=appt.date.year,
                        is_paid_to_doctor=appt.status == 'completed',
                    )
                    earning_count += 1
        
        self.stdout.write(f'  ✓ Created {payment_count} payments')
        self.stdout.write(f'  ✓ Created {earning_count} doctor earnings records')
