"""
Utility functions for data processing and encoding
"""


def map_yes_no_to_binary(value, default=0):
    """Convert 'Yes'/'No' to 1/0"""
    mapping = {'Yes': 1, 'No': 0}
    return mapping.get(value, default)


def encode_hospital_type(value, encoder_classes):
    """Encode hospital type using label encoder classes"""
    label_mapping = {label: idx for idx, label in enumerate(encoder_classes)}
    return label_mapping.get(str(value), -1)


def encode_feature_column(series, encoder_classes):
    """Encode feature column using label encoder classes"""
    label_mapping = {label: idx for idx, label in enumerate(encoder_classes)}
    return series.astype(str).map(label_mapping).fillna(-1).astype(int)


def format_doctor_response(row, specialization_name, specialization_encoder):
    """Format a doctor row into API response format"""
    return {
        'doctor_name': str(row['doctor_name']),
        'specialization': specialization_name,
        'rating_avg': float(row['rating_avg']),
        'experience_years': int(row['experience_years']),
        'consultation_fees': int(row['consultation_fees']),
        'predicted_score': float(row['predicted_score']),
        'hospital_name': str(row['hospital_name']),
        'full_address': str(row['full_address']),
    }


def validate_numeric(value, default=0, name='value'):
    """Validate and convert to numeric, with fallback"""
    try:
        result = int(value)
        if result < 0:
            result = default
        return result
    except (ValueError, TypeError):
        return default
