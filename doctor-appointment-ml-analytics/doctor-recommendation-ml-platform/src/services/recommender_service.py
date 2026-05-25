"""
Recommender Service - Main recommendation engine
"""
import warnings

from src.services.model_service import load_model_package, predict_scores
from src.services.data_service import load_doctor_data, filter_doctors_by_criteria
from src.utils import (
    encode_hospital_type,
    encode_feature_column,
    format_doctor_response,
    validate_numeric
)

warnings.filterwarnings('ignore')


def encode_features(temp_df, feature_encoders, le_hosp):
    """
    Encode features for model prediction
    
    Args:
        temp_df: Doctor dataframe
        feature_encoders: Dict of feature label encoders
        le_hosp: Hospital type label encoder
    
    Returns:
        Encoded features dataframe
    """
    x_temp = temp_df.copy()
    
    # Encode hospital type
    if 'hospital_type' in x_temp.columns:
        x_temp['hospital_type'] = x_temp['hospital_type'].apply(
            lambda v: encode_hospital_type(v, le_hosp.classes_)
        )
    
    # Encode other categorical features
    for col in x_temp.columns:
        if col in feature_encoders:
            encoder = feature_encoders[col]
            x_temp[col] = encode_feature_column(x_temp[col], encoder.classes_)
    
    return x_temp


def get_recommendations(user_input, top_n=None):
    """
    Get doctor recommendations based on user criteria
    
    Args:
        user_input: dict with keys: district, thana, specialization, max_fee, online, emergency
        top_n: Maximum number of results to return (None = all)
    
    Returns:
        dict with success flag and doctors list, or error message
    """
    try:
        # Load data and model
        package = load_model_package()
        df = load_doctor_data()
        
        model = package['model']
        le_spec = package['le_spec']
        le_hosp = package['le_hosp']
        feature_encoders = package['feature_encoders']
        features = package['features']
        
        # Validate max_fee
        max_fee = validate_numeric(user_input.get('max_fee', 2000), default=0, name='max_fee')
        
        # Filter doctors
        temp_df = filter_doctors_by_criteria(
            df,
            district=user_input['district'],
            thana=user_input['thana'],
            max_fee=max_fee,
            online=user_input.get('online', 0),
            emergency=user_input.get('emergency', 0)
        )
        
        # Check if doctors found after location/fee filtering
        if len(temp_df) == 0:
            return {'message': 'No doctors found with these criteria'}
        
        # Filter by specialization
        try:
            spec_encoded = le_spec.transform([user_input['specialization']])[0]
            temp_df = temp_df[temp_df['specialization_group'] == spec_encoded]
        except Exception:
            return {'error': 'Invalid specialization'}
        
        # Check if doctors found after specialization filtering
        if len(temp_df) == 0:
            return {'message': 'No doctors found with selected specialization'}
        
        # Encode features for prediction
        x_temp = temp_df[features].copy()
        x_temp = encode_features(x_temp, feature_encoders, le_hosp)
        
        # Get predictions
        temp_df['predicted_score'] = predict_scores(x_temp, model)
        
        # Sort by predicted score
        result = temp_df.sort_values(by='predicted_score', ascending=False)
        
        # Select relevant columns
        top_doctors = result[[
            'doctor_name',
            'specialization_group',
            'rating_avg',
            'experience_years',
            'consultation_fees',
            'predicted_score',
            'hospital_name',
            'full_address',
        ]]
        
        # Limit to top_n if specified
        if top_n is not None:
            top_doctors = top_doctors.head(top_n)
        
        # Format response
        recommendations = []
        for _, row in top_doctors.iterrows():
            spec_name = le_spec.classes_[int(row['specialization_group'])]
            doctor_dict = {
                'doctor_name': str(row['doctor_name']),
                'specialization': str(spec_name),
                'rating_avg': float(row['rating_avg']),
                'experience_years': int(row['experience_years']),
                'consultation_fees': int(row['consultation_fees']),
                'predicted_score': float(row['predicted_score']),
                'hospital_name': str(row['hospital_name']),
                'full_address': str(row['full_address']),
            }
            recommendations.append(doctor_dict)
        
        return {
            'success': True,
            'count': len(recommendations),
            'doctors': recommendations
        }
    
    except Exception as e:
        return {'error': str(e)}
