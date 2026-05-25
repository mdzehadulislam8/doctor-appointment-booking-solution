"""
Views for Commission Revenue Forecasting UI

Handles API calls and template rendering for user interface
"""

from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.contrib import messages
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# API endpoints
API_PREDICT = settings.API_PREDICT_ENDPOINT
API_FORECAST = settings.API_FORECAST_ENDPOINT


def get_api_data(endpoint, data):
    """
    Call API endpoint and return response data.
    
    Args:
        endpoint: API endpoint URL
        data: Dictionary of data to send
        
    Returns:
        tuple: (success, response_data, error_message)
    """
    try:
        logger.info(f"API Call: POST {endpoint}")
        logger.info(f"API Data: {data}")
        response = requests.post(endpoint, json=data, timeout=10)
        logger.info(f"API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            logger.info(f"API Success: {response.json()}")
            return True, response.json(), None
        elif response.status_code == 400:
            error = response.json().get('detail', 'Invalid input')
            logger.warning(f"API 400 Error: {error}")
            return False, None, f"Input Error: {error}"
        elif response.status_code == 503:
            logger.error("API Service Unavailable")
            return False, None, "API Service Unavailable. Make sure API is running."
        else:
            logger.error(f"API Error Status {response.status_code}: {response.text}")
            return False, None, f"API Error: Status {response.status_code}"
            
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Cannot connect to API at {endpoint}: {e}")
        return False, None, "Cannot connect to API. Make sure API is running at http://localhost:8000"
    except requests.exceptions.Timeout:
        logger.error(f"API request timeout to {endpoint}")
        return False, None, "API request timeout"
    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        return False, None, f"Error: {str(e)}"


@require_http_methods(["GET", "POST"])
def index(request):
    """
    Main page for commission revenue forecasting.
    Displays form and forecast results.
    """
    context = {
        'title': 'Commission Revenue Forecasting',
        'districts': [
            'Dhaka', 'Chattogram', 'Sylhet', 'Khulna',
            'Rajshahi', 'Barisal', 'Rangpur', 'Mymensingh'
        ],
        'specializations': [
            'Cardiologist', 'Neurologist', 'Orthopedic', 'General Physician',
            'Pediatrician', 'Dermatologist', 'ENT', 'Ophthalmologist',
            'Psychiatrist', 'Dentist'
        ],
        'hospital_types': [
            'Private Hospital', 'Government Hospital', 'Clinic', 'Diagnostic Center'
        ]
    }
    
    if request.method == 'POST':
        try:
            # Extract form data
            form_data = {
                'total_bookings': int(request.POST.get('total_bookings', 0)),
                'avg_fee': float(request.POST.get('avg_fee', 0)),
                'commission_rate': float(request.POST.get('commission_rate', 0)) / 100,
                'service_charge': float(request.POST.get('service_charge', 0)),
                'experience_years': 12,  # Default value
                'rating_avg': 4.7,  # Default value
                'district': request.POST.get('district', 'Dhaka'),
                'specialization_group': request.POST.get('specialization_group', 'General Physician'),
                'hospital_type': request.POST.get('hospital_type', 'Private Hospital'),
                'service_mode': request.POST.get('service_mode', 'Online'),
                'lag_1': float(request.POST.get('lag_1', 0)),
                'lag_7': float(request.POST.get('lag_7', 0)),
                'rolling_mean_7': float(request.POST.get('rolling_mean_7', 0)),
            }
            
            # Get forecast type
            forecast_type = request.POST.get('forecast_type', 'forecast')
            days = int(request.POST.get('days', 30))
            
            # Call appropriate API endpoint
            if forecast_type == 'predict':
                success, data, error = get_api_data(API_PREDICT, form_data)
                if success:
                    context['prediction'] = data['prediction']
                    context['currency'] = data.get('currency', 'BDT')
                    context['forecast_type'] = 'single_prediction'
                else:
                    messages.error(request, error)
            else:
                # Validate days
                if days < 1 or days > 365:
                    messages.error(request, "Days must be between 1 and 365")
                else:
                    endpoint = f"{API_FORECAST}?days={days}"
                    success, data, error = get_api_data(endpoint, form_data)
                    if success:
                        context['forecast'] = data
                        context['forecast_type'] = 'multi_forecast'
                    else:
                        messages.error(request, error)
            
            # Add form data back to context for form re-population
            context['form_data'] = form_data
            context['days'] = days
            context['commission_rate_percent'] = form_data['commission_rate'] * 100
            
            if 'forecast' in context:
                context['daily_average'] = context['forecast']['monthly_total'] / context['forecast']['total_days']
            
        except ValueError as e:
            messages.error(request, f"Invalid input: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing form: {str(e)}")
            messages.error(request, "An unexpected error occurred")
    
    return render(request, 'forecaster/index.html', context)
