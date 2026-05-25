import pickle as pk
import pandas as pd
import numpy as np
from pathlib import Path

# Get the project root (parent of notebooks folder)
PROJECT_ROOT = Path(__file__).parent.parent
MODELS_DIR = PROJECT_ROOT / "models"
DATA_DIR = PROJECT_ROOT / "data"

# Load the trained model and encoders
with open(MODELS_DIR / 'doctor_ai_full_package.pkl', 'rb') as f:
    package = pk.load(f)

model = package["model"]
le_spec = package["le_spec"]
le_hosp = package["le_hosp"]
feature_encoders = package["feature_encoders"]
features = package["features"]

# Load actual dataset from Excel file
df = pd.read_excel(DATA_DIR / "Dr.Seba_500_Organized_Final.xlsx")

# Preprocess the data
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Convert Yes/No columns to 1/0
df['online_consultation'] = df['online_consultation'].map({'Yes': 1, 'No': 0}).fillna(0).astype(int)
df['emergency_service'] = df['emergency_service'].map({'Yes': 1, 'No': 0}).fillna(0).astype(int)

# Encode specialization_group in the dataset
df['specialization_group'] = le_spec.transform(df['specialization_group'].astype(str))


def recommend_from_pickle(user_input, df, model, top_n=5):
    """
    Recommend doctors based on user input using the trained model
    """
    temp_df = df.copy()

    # Filter by location
    temp_df = temp_df[
        (temp_df['district'] == user_input['district']) &
        (temp_df['thana'] == user_input['thana'])
    ]

    # Filter by consultation fee
    temp_df = temp_df[temp_df['consultation_fees'] <= user_input['max_fee']]

    # Filter by online consultation if needed
    if user_input['online'] == 1:
        temp_df = temp_df[temp_df['online_consultation'] == 1]

    # Filter by emergency service if needed
    if user_input['emergency'] == 1:
        temp_df = temp_df[temp_df['emergency_service'] == 1]

    # Encode specialization
    try:
        spec_encoded = le_spec.transform([user_input['specialization']])[0]
        temp_df = temp_df[temp_df['specialization_group'] == spec_encoded]
    except:
        return "Specialization not found"

    if len(temp_df) == 0:
        return "No doctors found with given criteria"

    # Prepare features for prediction
    X_temp = temp_df[features].copy()
    
    # Encode hospital_type using le_hosp
    if 'hospital_type' in X_temp.columns:
        hosp_type_mapping = {label: idx for idx, label in enumerate(le_hosp.classes_)}
        X_temp['hospital_type'] = X_temp['hospital_type'].astype(str).map(hosp_type_mapping).fillna(-1).astype(int)
    
    # Encode other categorical features from feature_encoders
    for col in X_temp.columns:
        if col in feature_encoders:
            encoder = feature_encoders[col]
            label_mapping = {label: idx for idx, label in enumerate(encoder.classes_)}
            X_temp[col] = X_temp[col].astype(str).map(label_mapping).fillna(-1).astype(int)

    # Make predictions
    temp_df['predicted_score'] = model.predict(X_temp)

    # Sort by predicted score (descending)
    result = temp_df.sort_values(by='predicted_score', ascending=False)

    return result[['doctor_name', 'rating_avg', 'experience_years', 'consultation_fees', 'predicted_score', 'hospital_name', 'full_address']].head(top_n)


def print_doctor_recommendations(result):
    """Print doctor recommendations in a nicely formatted table"""
    if isinstance(result, str):
        print(f"{result}\n")
        return
    
    # Print header
    print("\n{:<25} {:<12} {:<18} {:<20} {:<15} {:<35} {:<40}".format(
        "doctor_name", "rating_avg", "experience_years", "consultation_fees", "predicted_score", "hospital_name", "full_address"
    ))
    print("-" * 180)
    
    # Print each row
    for idx, row in result.iterrows():
        print("{:<25} {:<12.2f} {:<18} {:<20} {:<15.6f} {:<35} {:<40}".format(
            str(row['doctor_name'])[:24],
            row['rating_avg'],
            str(int(row['experience_years'])),
            str(int(row['consultation_fees'])),
            row['predicted_score'],
            str(row['hospital_name'])[:34],
            str(row['full_address'])[:39]
        ))
    print()


# Test with different search criteria
if __name__ == "__main__":
    # Set pandas display options for full output
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)
    
    print("="*150)
    print("DOCTOR RECOMMENDATION SYSTEM - ACTUAL DATASET (500 Doctors)")
    print("="*150)
    
    # Test Case 1
    print("\n[TEST CASE 1] Surgeons in Barisal, Bakerganj")
    print("-" * 150)
    user_input = {
        'district': 'Barisal',
        'thana': 'Bakerganj',
        'specialization': 'Surgeon',
        'max_fee': 2000,
        'online': 0,
        'emergency': 0
    }
    
    print(f"Location: {user_input['district']}, {user_input['thana']} | Specialization: {user_input['specialization']} | Max Fee: {user_input['max_fee']}")
    result = recommend_from_pickle(user_input, df, model, top_n=5)
    print_doctor_recommendations(result)
    
    # Test Case 2
    print("\n[TEST CASE 2] Cardiologists in Dhaka with budget <= 1500")
    print("-" * 150)
    user_input = {
        'district': 'Dhaka',
        'thana': 'Motijheel',
        'specialization': 'Cardiologist',
        'max_fee': 1500,
        'online': 0,
        'emergency': 0
    }
    
    print(f"Location: {user_input['district']}, {user_input['thana']} | Specialization: {user_input['specialization']} | Max Fee: {user_input['max_fee']}")
    result = recommend_from_pickle(user_input, df, model, top_n=5)
    print_doctor_recommendations(result)
    
    # Test Case 3
    print("\n[TEST CASE 3] Pediatricians in Chattogram with online consultation")
    print("-" * 150)
    user_input = {
        'district': 'Barisal',
        'thana': 'Bakerganj',
        'specialization': 'Surgeon',
        'max_fee': 1500,
        'online': 0,
        'emergency': 0
    }
    
    print(f"Location: {user_input['district']}, {user_input['thana']} | Specialization: {user_input['specialization']} | Max Fee: {user_input['max_fee']} | Online: Yes")
    result = recommend_from_pickle(user_input, df, model, top_n=5)
    print_doctor_recommendations(result)
    
    print("="*150)
