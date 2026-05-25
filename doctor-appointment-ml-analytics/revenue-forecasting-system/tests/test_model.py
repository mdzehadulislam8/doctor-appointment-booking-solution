"""
Commission Revenue Forecasting Model - Test Script

Tests the loaded model with multi-output predictions (Daily, Weekly, Monthly).
This module demonstrates how to load the pre-trained CatBoost model
and generate forecasts for commission revenue at multiple time horizons.

Author: Data Science Team
Version: 1.0.0
"""

import pickle
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class CommissionForecaster:
    """
    Commission Revenue Forecasting Model
    
    Loads a pre-trained CatBoost model and generates multi-step forecasts
    for commission revenue with daily, weekly, and monthly aggregations.
    
    Attributes:
        model: Trained CatBoost regressor model
        features: List of feature names used by the model
        mappings: Dictionary of categorical feature mappings
    """
    
    def __init__(self, model_path):
        """
        Initialize the forecaster with a trained model.
        
        Args:
            model_path (str or Path): Path to the pickled model file
            
        Raises:
            FileNotFoundError: If model file does not exist
            ValueError: If model data is invalid
        """
        model_path = Path(model_path)
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            logger.info(f"✓ Model loaded successfully from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise ValueError(f"Cannot load model from {model_path}: {e}")
        
        # Extract components from the model dictionary
        if isinstance(model_data, dict):
            self.model = model_data.get('model')
            self.features = model_data.get('features')
            self.mappings = model_data.get('mappings')
            
            if self.model is None:
                raise ValueError("Model dictionary missing 'model' key")
            if self.features is None:
                raise ValueError("Model dictionary missing 'features' key")
                
            logger.info(f"✓ Model type: {type(self.model).__name__}")
            logger.info(f"✓ Using {len(self.features)} features")
        else:
            raise ValueError("Invalid model format: expected dictionary with 'model', 'features' keys")
    
    def encode_input(self, user_data):
        """
        Encode categorical features for model prediction.
        
        Args:
            user_data (dict): Input data with categorical values
            
        Returns:
            dict: Encoded input data ready for prediction
        """
        data = user_data.copy()
        
        if self.mappings:
            # Use saved mappings
            if 'district' in self.mappings and 'district' in data:
                data['district'] = self.mappings['district'].get(data['district'], 1)
            if 'specialization_group' in self.mappings and 'specialization_group' in data:
                data['specialization_group'] = self.mappings['specialization_group'].get(
                    data['specialization_group'], 4
                )
            if 'hospital_type' in self.mappings and 'hospital_type' in data:
                data['hospital_type'] = self.mappings['hospital_type'].get(data['hospital_type'], 1)
        else:
            # Use default mappings
            district_map = {
                'Dhaka': 1, 'Chattogram': 2, 'Sylhet': 3, 'Khulna': 4,
                'Rajshahi': 5, 'Barisal': 6, 'Rangpur': 7, 'Mymensingh': 8
            }
            data['district'] = district_map.get(data.get('district', 'Dhaka'), 1)
            
            specialization_map = {
                'Cardiologist': 1, 'Neurologist': 2, 'Orthopedic': 3, 'General Physician': 4,
                'Pediatrician': 5, 'Dermatologist': 6, 'ENT': 7, 'Ophthalmologist': 8,
                'Psychiatrist': 9, 'Dentist': 10
            }
            data['specialization_group'] = specialization_map.get(
                data.get('specialization_group', 'General Physician'), 4
            )
            
            hospital_map = {
                'Private Hospital': 1, 'Government Hospital': 2, 'Clinic': 3, 'Diagnostic Center': 4
            }
            data['hospital_type'] = hospital_map.get(data.get('hospital_type', 'Private Hospital'), 1)
        
        return data
    
    def forecast(self, user_input, days=30):
        """
        Generate multi-step ahead forecast.
        
        Args:
            user_input (dict): Input features for prediction
            days (int): Number of days to forecast (default: 30)
            
        Returns:
            list: Forecast predictions for each day
            
        Raises:
            ValueError: If input is invalid or prediction fails
        """
        if not isinstance(user_input, dict):
            raise ValueError("Input must be a dictionary")
        if days <= 0:
            raise ValueError("Days must be positive")
        
        current_input = self.encode_input(user_input.copy())
        preds = []
        
        try:
            for i in range(days):
                df_input = pd.DataFrame([current_input])
                df_input = df_input[self.features]
                
                pred = self.model.predict(df_input)[0]
                preds.append(pred)
                
                # Update lag features for next prediction
                current_input['lag_7'] = current_input['lag_1']
                current_input['lag_1'] = pred
                current_input['rolling_mean_7'] = (current_input['rolling_mean_7'] * 6 + pred) / 7
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise ValueError(f"Forecast generation failed: {e}")
        
        return preds


def display_forecast(user_input, forecast):
    """
    Display forecast results in a formatted way.
    
    Args:
        user_input (dict): Input data used for prediction
        forecast (list): Forecast predictions
    """
    print("=" * 60)
    print("INPUT DATA:")
    print("=" * 60)
    for key, value in user_input.items():
        print(f"  {key}: {value}")
    print()
    
    print("=" * 60)
    print(f"FORECAST RESULTS ({len(forecast)} days)")
    print("=" * 60)
    print()
    
    # Daily output (first 7 days)
    print("📅 DAILY FORECAST (Next 7 Days):")
    print("-" * 60)
    for i in range(min(7, len(forecast))):
        print(f"  Day {i+1}: ৳ {round(forecast[i], 2):,.2f}")
    print()
    
    # Weekly output
    weekly = sum(forecast[:7])
    print("📊 WEEKLY FORECAST:")
    print("-" * 60)
    print(f"  Total (7 days): ৳ {round(weekly, 2):,.2f}")
    print(f"  Daily Average: ৳ {round(weekly/7, 2):,.2f}")
    print()
    
    # Monthly output
    monthly = sum(forecast)
    print("📈 MONTHLY FORECAST:")
    print("-" * 60)
    print(f"  Total ({len(forecast)} days): ৳ {round(monthly, 2):,.2f}")
    print(f"  Daily Average: ৳ {round(monthly/len(forecast), 2):,.2f}")
    print(f"  Weekly Average: ৳ {round(monthly/(len(forecast)/7), 2):,.2f}")
    print()
    
    # Statistics
    print("📉 PREDICTION STATISTICS:")
    print("-" * 60)
    print(f"  Min Daily: ৳ {round(min(forecast), 2):,.2f}")
    print(f"  Max Daily: ৳ {round(max(forecast), 2):,.2f}")
    print(f"  Std Dev: ৳ {round(np.std(forecast), 2):,.2f}")
    print(f"  Mean Daily: ৳ {round(np.mean(forecast), 2):,.2f}")
    print()


def main():
    """Main function to run the forecast test."""
    try:
        # Get model path (parent directory of tests folder)
        model_path = Path(__file__).parent.parent / 'models' / 'commission_revenue_forecasting_model.pkl'
        
        # Initialize forecaster
        forecaster = CommissionForecaster(model_path)
        
        # Test input data
        user_input_test = {
            'total_bookings': 180,
            'avg_fee': 700,
            'commission_rate': 0.12,
            'service_charge': 60,
            'experience_years': 12,
            'rating_avg': 4.7,
            'district': 'Chattogram',
            'specialization_group': 'Neurologist',
            'hospital_type': 'Private Hospital',
            'lag_1': 9500,
            'lag_7': 8800,
            'rolling_mean_7': 9000
        }
        
        # Generate forecast
        logger.info("Running 30-day forecast...")
        forecast = forecaster.forecast(user_input_test, days=30)
        
        # Display results
        display_forecast(user_input_test, forecast)
        
        logger.info("✓ Test completed successfully!")
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"File error: {e}")
        return 1
    except ValueError as e:
        logger.error(f"Value error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
