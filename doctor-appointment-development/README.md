# DrSeba.com - Healthcare Platform

A comprehensive healthcare appointment booking platform for Bangladesh built with Django and Bootstrap.

## Features

### User Roles
- **Patient**: Browse doctors, book appointments, manage profile
- **Doctor**: Manage profile, availability, appointments, view earnings
- **Super Admin**: Full system control, user management, statistics
- **Employee**: Booking confirmation capabilities

### Core Features
- Doctor directory with search and filter
- Appointment booking system with cart functionality
- Multiple payment options (bKash, Nagad, Card, Cash)
- Bilingual support (English & Bangla)
- Dark mode support
- Invoice generation
- Rating and review system
- BMDC verification badges

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd drseba
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create superuser:
```bash
python manage.py createsuperuser
```

6. Run development server:
```bash
python manage.py runserver
```

## Usage

### Default Admin Credentials
After creating superuser, you can access the admin panel at `/admin/`

### User Registration
- Patients can register directly
- Doctors need verification after registration

### Phone Number Format
All phone numbers must be in Bangladesh format: `+8801XXXXXXXXX`

## Employee Dashboard

The Employee Dashboard allows staff members to:
- View and confirm pending appointments
- Monitor daily statistics (pending, confirmed, total appointments)
- Access all platform appointments from a centralized interface
- Quick action buttons to process appointments efficiently

**Quick Access**:
```
URL: http://127.0.0.1:8000/dashboard/employee/
Login: Username: rahima | Password: demo123456
```

For detailed guide, see [EMPLOYEE_DASHBOARD_GUIDE.md](EMPLOYEE_DASHBOARD_GUIDE.md) and [EMPLOYEE_DASHBOARD_IMPLEMENTATION.md](EMPLOYEE_DASHBOARD_IMPLEMENTATION.md)

## Project Structure

```
drseba/
├── drseba/              # Project settings
├── accounts/            # User authentication and profiles
├── doctors/             # Doctor profiles and specialties
├── appointments/        # Appointment booking system
├── payments/            # Payment processing and invoices
├── dashboards/          # User dashboards
├── templates/           # HTML templates
├── static/              # Static files (CSS, JS, images)
└── manage.py
```

## License

This project is licensed under the MIT License.
