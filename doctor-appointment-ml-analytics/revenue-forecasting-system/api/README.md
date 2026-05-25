# Commission Revenue Forecasting API

Professional REST API for commission revenue predictions built with FastAPI.

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Run API Server

```bash
# Start the API
python main.py

# Or with custom host/port
uvicorn main:app --host 0.0.0.0 --port 8000

# With auto-reload during development
uvicorn main:app --reload
```

The API will be available at: `http://localhost:8000`

## Endpoints

### 1. Health Check
```
GET /health
```

Check if the API and model are ready.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "service": "Commission Revenue Forecasting API"
}
```

---

### 2. Single Day Prediction
```
POST /predict
```

Get commission revenue prediction for the next single day.

**Request:**
```json
{
  "total_bookings": 180,
  "avg_fee": 700,
  "commission_rate": 0.12,
  "experience_years": 12,
  "rating_avg": 4.7,
  "district": "Chattogram",
  "specialization_group": "Neurologist",
  "hospital_type": "Private Hospital",
  "lag_1": 9500,
  "lag_7": 8800,
  "rolling_mean_7": 9000
}
```

**Response:**
```json
{
  "prediction": 13343.95,
  "currency": "BDT",
  "message": "Single day prediction successful"
}
```

---

### 3. Multi-Day Forecast
```
POST /forecast?days=30
```

Get commission revenue forecast for multiple days with daily, weekly, and monthly summaries.

**Query Parameters:**
- `days` (optional): Number of days to forecast (1-365, default: 30)

**Request:**
```json
{
  "total_bookings": 180,
  "avg_fee": 700,
  "commission_rate": 0.12,
  "experience_years": 12,
  "rating_avg": 4.7,
  "district": "Chattogram",
  "specialization_group": "Neurologist",
  "hospital_type": "Private Hospital",
  "lag_1": 9500,
  "lag_7": 8800,
  "rolling_mean_7": 9000
}
```

**Response:**
```json
{
  "daily_forecast": [13343.95, 13259.62, 13179.30, 13120.13, 13125.30, 13184.46, 13184.46],
  "weekly_total": 92397.23,
  "monthly_total": 395257.95,
  "total_days": 30,
  "daily_statistics": {
    "min": 13120.13,
    "max": 13343.95,
    "mean": 13175.26,
    "std_dev": 45.65
  },
  "weekly_breakdown": [92397.23, 91998.15, 92043.64, 92407.64, 26411.29],
  "currency": "BDT",
  "message": "Forecast completed successfully"
}
```

---

## Example Usage (Python)

```python
import requests

# API endpoint
BASE_URL = "http://localhost:8000"

# Commissioner data
data = {
    "total_bookings": 180,
    "avg_fee": 700,
    "commission_rate": 0.12,
    "experience_years": 12,
    "rating_avg": 4.7,
    "district": "Chattogram",
    "specialization_group": "Neurologist",
    "hospital_type": "Private Hospital",
    "lag_1": 9500,
    "lag_7": 8800,
    "rolling_mean_7": 9000
}

# Single prediction
response = requests.post(f"{BASE_URL}/predict", json=data)
prediction = response.json()
print(f"Next day prediction: {prediction['prediction']} {prediction['currency']}")

# 30-day forecast
response = requests.post(f"{BASE_URL}/forecast?days=30", json=data)
forecast = response.json()
print(f"30-day total: {forecast['monthly_total']} {forecast['currency']}")
print(f"Weekly average: {forecast['weekly_total']} {forecast['currency']}")
```

---

## Example Usage (cURL)

```bash
# Single prediction
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "total_bookings": 180,
    "avg_fee": 700,
    "commission_rate": 0.12,
    "experience_years": 12,
    "rating_avg": 4.7,
    "district": "Chattogram",
    "specialization_group": "Neurologist",
    "hospital_type": "Private Hospital",
    "lag_1": 9500,
    "lag_7": 8800,
    "rolling_mean_7": 9000
  }'

# 30-day forecast
curl -X POST "http://localhost:8000/forecast?days=30" \
  -H "Content-Type: application/json" \
  -d '{
    "total_bookings": 180,
    "avg_fee": 700,
    "commission_rate": 0.12,
    "experience_years": 12,
    "rating_avg": 4.7,
    "district": "Chattogram",
    "specialization_group": "Neurologist",
    "hospital_type": "Private Hospital",
    "lag_1": 9500,
    "lag_7": 8800,
    "rolling_mean_7": 9000
  }'
```

---

## Interactive Documentation

FastAPI provides interactive API documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

You can test all endpoints directly from your browser!

---

## Supported Districts

- Dhaka
- Chattogram
- Sylhet
- Khulna
- Rajshahi
- Barisal
- Rangpur
- Mymensingh

## Supported Specializations

- Cardiologist
- Neurologist
- Orthopedic
- General Physician
- Pediatrician
- Dermatologist
- ENT
- Ophthalmologist
- Psychiatrist
- Dentist

## Supported Hospital Types

- Private Hospital
- Government Hospital
- Clinic
- Diagnostic Center

---

## Error Handling

The API returns appropriate HTTP status codes:

- **200**: Success
- **400**: Bad request (invalid input)
- **500**: Internal server error
- **503**: Service unavailable (model not loaded)

Error response format:
```json
{
  "detail": "Error description"
}
```

---

## Performance

- Response time: ~100-500ms per request
- Model size: ~100MB
- Supported concurrent requests: Unlimited (with uvicorn workers)

---

## Version

API v1.0.0

---

## Author

Data Science Team
