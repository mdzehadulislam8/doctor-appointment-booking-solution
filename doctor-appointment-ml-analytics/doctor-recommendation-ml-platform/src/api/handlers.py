"""
API Handlers - View functions for API endpoints
"""
import json
import warnings
from functools import wraps

import pandas as pd
from django.http import FileResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods

from src.constants import DEMO_UI_DIR, DEFAULT_TOP_N
from src.services.data_service import get_options_data, get_thanas_for_district
from src.services.recommender_service import get_recommendations
from src.api.schemas import DoctorRecommendationRequest, RecommendationsResponse

warnings.filterwarnings('ignore')


# ============================================================================
# HOME PAGE HANDLERS
# ============================================================================

@require_http_methods(['GET', 'POST'])
def home(request):
    """Serve main doctor search page with Django-based pagination"""
    options = get_options_data()
    
    selected_district = request.POST.get('district') or (options['districts'][0] if options['districts'] else '')
    thanas_for_selected = get_thanas_for_district(selected_district) if selected_district else []
    selected_thana = request.POST.get('thana') or (thanas_for_selected[0] if thanas_for_selected else '')
    
    if selected_thana not in thanas_for_selected and thanas_for_selected:
        selected_thana = thanas_for_selected[0]
    
    selected_spec = request.POST.get('specialization') or (
        options['specializations'][0] if options['specializations'] else ''
    )
    if selected_spec not in options['specializations'] and options['specializations']:
        selected_spec = options['specializations'][0]
    
    max_fee = request.POST.get('maxFee', '2000')
    online = request.POST.get('online') == 'on'
    emergency = request.POST.get('emergency') == 'on'
    top_n = None
    
    # Django pagination control
    show_all = request.POST.get('show_all') == 'true'
    initial_display = 4  # Show 4 doctors by default

    context = {
        'districts': options['districts'],
        'specializations': options['specializations'],
        'thanas': thanas_for_selected,
        'selected_district': selected_district,
        'selected_thana': selected_thana,
        'selected_spec': selected_spec,
        'max_fee': max_fee,
        'online': online,
        'emergency': emergency,
        'top_n': top_n,
        'searched': False,
        'error': '',
        'doctors': [],
        'displayed_doctors': [],  # Limited set for initial display
        'show_see_more_btn': False,  # Show "See More" button
    }

    if request.method == 'POST':
        context['searched'] = True
        try:
            max_fee_int = int(max_fee)
            if max_fee_int < 0:
                max_fee_int = 0

            payload = {
                'district': selected_district,
                'thana': selected_thana,
                'specialization': selected_spec,
                'max_fee': max_fee_int,
                'online': 1 if online else 0,
                'emergency': 1 if emergency else 0,
            }
            result = get_recommendations(payload, top_n)
            if result.get('success'):
                all_doctors = result['doctors']
                context['doctors'] = all_doctors
                
                # Django-based pagination logic
                if show_all:
                    # Show all doctors
                    context['displayed_doctors'] = all_doctors
                    context['show_see_more_btn'] = False
                else:
                    # Show only first 4 doctors, display "See More" button if more exist
                    context['displayed_doctors'] = all_doctors[:initial_display]
                    context['show_see_more_btn'] = len(all_doctors) > initial_display
            else:
                context['error'] = result.get('message') or result.get('error') or 'No doctors found'
        except Exception as exc:
            context['error'] = str(exc)

    return render(request, 'index.html', context)


@require_GET
def style_css(request):
    """Serve CSS stylesheet"""
    return FileResponse(open(DEMO_UI_DIR / 'style.css', 'rb'), content_type='text/css')


# ============================================================================
# API ENDPOINTS
# ============================================================================

@require_GET
def api_root(request):
    """API root information"""
    return JsonResponse({
        'status': 'healthy',
        'message': 'Doctor Recommendation API is running',
        'endpoints': [
            '/api/health',
            '/api/options',
            '/api/thanas/<district>',
            '/api/recommendations',
        ],
    })


@require_GET
def api_health(request):
    """Health check endpoint"""
    return JsonResponse({'status': 'healthy'})


@require_GET
def api_options(request):
    """Get all available options (districts, thanas, specializations)"""
    return JsonResponse({'success': True, 'options': get_options_data()})


@require_GET
def api_thanas(request, district):
    """Get thanas for a specific district"""
    thanas = get_thanas_for_district(district)
    if not thanas:
        return JsonResponse({'error': f'No thanas found for {district}'}, status=404)
    return JsonResponse({'district': district, 'thanas': thanas})


@csrf_exempt
@require_http_methods(['POST'])
def api_recommendations(request):
    """Get doctor recommendations based on criteria"""
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

    # Validate request
    validator = DoctorRecommendationRequest(data)
    if not validator.validate():
        return JsonResponse({'error': ' | '.join(validator.get_errors())}, status=400)

    top_n = data.get('top_n', DEFAULT_TOP_N)
    result = get_recommendations(data, top_n)

    if 'error' in result:
        return JsonResponse(result, status=400)
    
    return JsonResponse(result)
