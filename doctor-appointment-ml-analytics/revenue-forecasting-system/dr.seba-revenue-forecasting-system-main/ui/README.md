# Commission Revenue Forecasting UI

Django-based user interface for commission revenue predictions. This UI connects to the FastAPI backend to provide an interactive forecasting experience.

## Features

- Beautiful, responsive web interface
- Real-time API integration with FastAPI backend
- Single day predictions and multi-day forecasts
- Comprehensive forecast statistics
- Support for various medical specializations and locations
- Forecast history tracking (optional)

## Technology Stack

- **Backend Framework**: Django 4.2+
- **Frontend**: HTML5 + CSS3 (fully responsive)
- **API Client**: Python requests library
- **No JavaScript required** - Pure Django templating

## Installation

### Prerequisites

- Python 3.8+
- Virtual environment
- Commission Revenue Forecasting API running on port 8000

### Setup

```bash
# Navigate to UI directory
cd ui

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

## Running the UI

```bash
# Start the Django development server
python manage.py runserver 8001

# Access the UI at http://localhost:8001
```

The UI will automatically connect to the API at `http://localhost:8000`

## File Structure

```
ui/
├── manage.py                     # Django management script
├── requirements.txt              # Python dependencies
├── db.sqlite3                    # SQLite database
├── forecasting_ui/
│   ├── settings.py              # Django settings
│   ├── urls.py                  # URL configuration
│   ├── wsgi.py                  # WSGI configuration
│   ├── __init__.py
│   ├── templates/
│   │   └── forecaster/
│   │       └── index.html       # Main UI template
│   └── static/
│       └── css/
│           └── style.css        # CSS styles
├── forecaster/
│   ├── models.py                # Django models
│   ├── views.py                 # View logic (API integration)
│   ├── apps.py                  # App configuration
│   ├── urls.py                  # App URLs
│   └── __init__.py
└── README.md                    # This file
```

## How It Works

### User Flow

1. **User enters data** via the HTML form
2. **Django view receives** the form data
3. **View calls API** using Python `requests` library
4. **API returns** prediction or forecast
5. **Django renders** response in HTML template
6. **User sees** results on the same page

### API Integration

The UI communicates with the FastAPI backend:

```python
# API Endpoints used
POST /predict          # Single day prediction
POST /forecast?days=X  # Multi-day forecast
```

Data flow:
```
Form Input → Django View → API Request → API Response → HTML Template
```

## Key Django Components

### Settings (`forecasting_ui/settings.py`)
- Django app configuration
- Template directories
- Static files configuration
- API endpoints configuration

### Views (`forecaster/views.py`)
- `index()` - Main view handling form display and API calls
- `get_api_data()` - API communication helper

### Templates (`forecasting_ui/templates/forecaster/index.html`)
- Responsive form with all input fields
- Results display sections
- Error and success message handling
- Support for both single predictions and multi-day forecasts

### Styles (`forecasting_ui/static/css/style.css`)
- Fully responsive design
- Mobile-friendly layout
- Gradient backgrounds
- Smooth animations
- Professional color scheme

## Usage Examples

### Running Forecast

1. Open http://localhost:8001
2. Fill in commissioner details:
   - Bookings, fees, ratings
   - Professional information
   - Historical revenue data
3. Select forecast type:
   - Single Day Prediction
   - Multi-Day Forecast (1-365 days)
4. Click "Generate Forecast"
5. View results instantly

### Form Validation

- All fields are validated on the server side
- Invalid inputs show error messages
- Form re-populates with submitted data for correction

### Error Handling

The UI handles various error scenarios:
- API connection errors
- Invalid input data
- API service unavailability
- Request timeouts

## Django Features Used

- **Forms**: Custom form handling with CSRF protection
- **Templates**: Jinja2 templating with filters
- **Views**: Function-based views with decorators
- **Static Files**: CSS organization
- **Messages Framework**: Error/success notifications
- **Settings**: Environment-based configuration

## No JavaScript

This UI uses **zero JavaScript**. All functionality is handled through:
- Django server-side rendering
- HTML form submissions
- CSS for styling and basic animations
- Django template filters for data transformation

## Deployment

For production deployment:

```bash
# Collect static files
python manage.py collectstatic

# Use production WSGI server (gunicorn, uWSGI, etc.)
pip install gunicorn
gunicorn forecasting_ui.wsgi:application --bind 0.0.0.0:8001
```

## Configuration

### API Connection

Edit `forecasting_ui/settings.py`:

```python
API_BASE_URL = 'http://localhost:8000'  # API server address
API_PREDICT_ENDPOINT = f'{API_BASE_URL}/predict'
API_FORECAST_ENDPOINT = f'{API_BASE_URL}/forecast'
```

### Django Settings

- Debug mode: Change `DEBUG = False` for production
- Allowed hosts: Modify `ALLOWED_HOSTS` for production
- Secret key: Use environment variable in production

## Supported Features

✅ Single day commission prediction  
✅ Multi-day revenue forecasting (1-365 days)  
✅ Real-time statistics and analysis  
✅ Daily, weekly, and monthly breakdowns  
✅ Professional specialization filtering  
✅ Geographic location support  
✅ Historical data integration  
✅ Responsive mobile design  
✅ Error handling and validation  
✅ No external JavaScript dependencies  

## Troubleshooting

### Problem: "Cannot connect to API"
- Ensure API is running on http://localhost:8000
- Check firewall settings
- Verify API is accessible

### Problem: Port 8001 already in use
```bash
python manage.py runserver 8001  # Use different port
```

### Problem: Database errors
```bash
python manage.py migrate
python manage.py makemigrations
```

## Requirements Specification

- ✅ Django-based UI
- ✅ HTML + CSS (no JavaScript)
- ✅ Connects to FastAPI backend
- ✅ Input form for all parameters
- ✅ Displays daily, weekly, monthly outputs
- ✅ Professional design
- ✅ Error handling
- ✅ No API modifications

## Version

UI v1.0.0

## Author

Data Science Team


