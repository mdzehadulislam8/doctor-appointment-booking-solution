"""
Request and Response Schemas
"""


class DoctorRecommendationRequest:
    """Request schema for doctor recommendations"""
    
    REQUIRED_FIELDS = ['district', 'thana', 'specialization', 'max_fee', 'online', 'emergency']
    
    def __init__(self, data):
        self.data = data
        self.errors = []
    
    def validate(self):
        """Validate request data"""
        for field in self.REQUIRED_FIELDS:
            if field not in self.data:
                self.errors.append(f'Missing required field: {field}')
        
        # Validate numeric fields
        try:
            max_fee = int(self.data.get('max_fee', 0))
            if max_fee < 0:
                self.errors.append('max_fee must be non-negative')
        except (ValueError, TypeError):
            self.errors.append('max_fee must be numeric')
        
        return len(self.errors) == 0
    
    def get_errors(self):
        return self.errors


class DoctorResponse:
    """Doctor response object"""
    
    @staticmethod
    def from_row(doctor_dict):
        """Create response from doctor data"""
        return {
            'doctor_name': doctor_dict.get('doctor_name', ''),
            'specialization': doctor_dict.get('specialization', ''),
            'rating_avg': doctor_dict.get('rating_avg', 0.0),
            'experience_years': doctor_dict.get('experience_years', 0),
            'consultation_fees': doctor_dict.get('consultation_fees', 0),
            'predicted_score': doctor_dict.get('predicted_score', 0.0),
            'hospital_name': doctor_dict.get('hospital_name', ''),
            'full_address': doctor_dict.get('full_address', ''),
        }


class RecommendationsResponse:
    """Recommendations list response"""
    
    @staticmethod
    def success(doctors_list, count=None):
        """Generate success response"""
        return {
            'success': True,
            'count': count or len(doctors_list),
            'doctors': doctors_list
        }
    
    @staticmethod
    def error(message, error_type='error'):
        """Generate error response"""
        return {
            'success': False,
            error_type: message
        }
