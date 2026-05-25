# Dr. Seba Revenue Forecasting System

> Production-oriented revenue forecasting platform for healthcare professionals, built with FastAPI, Django, and a CatBoost regression model.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-009688?style=flat-square)](https://fastapi.tiangolo.com/)
[![Django](https://img.shields.io/badge/Django-4.x-0C4B33?style=flat-square)](https://www.djangoproject.com/)
[![CatBoost](https://img.shields.io/badge/ML-CatBoost-orange?style=flat-square)](https://catboost.ai/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen?style=flat-square)](https://github.com/mdzehadulislam8/drseba-revenue-forecasting-system)

---

## Overview

Dr. Seba Revenue Forecasting System predicts commission revenue for healthcare professionals using booking volume, pricing, service charge, experience, ratings, district, specialization, hospital type, and recent historical trends. The system supports both single-day predictions and multi-day forecasts through a simple Django web interface and a FastAPI backend.

The application is split into two services:

- `api/` provides the FastAPI prediction service on port `8000`.
- `ui/` provides the Django user interface on port `8001`.

This separation keeps the prediction logic independent from the presentation layer and makes the system easier to test, debug, and deploy.

---

## Key Features

- Single-day revenue prediction from a structured input form.
- Multi-day forecasting with daily, weekly, and monthly summaries.
- FastAPI backend with validation, Swagger docs, and JSON responses.
- Django frontend for interactive input and result rendering.
- CatBoost-based regression model for numerical forecasting.
- Responsive dashboard-style UI.
- SQLite-backed application state for local development.
- Windows helper scripts for startup and shutdown.

---

## Input and Output Preview

The screenshot below shows the relationship between the input form and the generated output panel.

<p align="center">
  <a href="https://drive.google.com/file/d/1Ao9-6y_8CuRetGJntJwaB4-0sSJxutZS/view?usp=drive_link" target="_blank" rel="noreferrer">
    <img src="https://drive.google.com/uc?export=view&id=1Ao9-6y_8CuRetGJntJwaB4-0sSJxutZS" alt="Input and output preview" width="1000" />
  </a>
</p>

<p align="center">
  <strong>Input form on the left, prediction output on the right.</strong>
</p>

If the image does not render directly in your preview, use the Drive link above. The section is included to visually connect the form inputs with the forecast outputs shown to the user.

---

## Architecture

```text
User
  -> Django UI (Port 8001)
      -> FastAPI Backend (Port 8000)
          -> Pydantic Validation
          -> CatBoost Model Inference
          -> JSON Response
      -> Rendered Forecast Results
```

### Layers

| Layer | Responsibility |
|-------|----------------|
| UI Layer | Collects user input and renders prediction output |
| API Layer | Validates requests and serves prediction endpoints |
| ML Layer | Runs the trained CatBoost model |
| Data Layer | Stores Django application state in SQLite |

---

## Input Data Contract

The API accepts the following core fields:

| Field | Type | Description |
|-------|------|-------------|
| `total_bookings` | integer | Total appointments in the selected period |
| `avg_fee` | float | Average consultation fee |
| `commission_rate` | float | Commission percentage as a decimal |
| `service_charge` | float | Additional per-service charge |
| `experience_years` | integer | Years of professional experience |
| `rating_avg` | float | Average user or patient rating |
| `district` | string | Operating district |
| `specialization_group` | string | Medical specialization group |
| `hospital_type` | string | Institution type |
| `lag_1` | float | Previous day revenue |
| `lag_7` | float | Revenue from seven days ago |
| `rolling_mean_7` | float | Seven-day rolling mean |

Example request payload:

```json
{
  "total_bookings": 180,
  "avg_fee": 700,
  "commission_rate": 0.12,
  "service_charge": 60,
  "experience_years": 12,
  "rating_avg": 4.7,
  "district": "Dhaka",
  "specialization_group": "General Physician",
  "hospital_type": "Private Hospital",
  "lag_1": 9500,
  "lag_7": 8800,
  "rolling_mean_7": 9000
}
```

---

## Output Format

### Single Prediction

```json
{
  "prediction": 23429.77,
  "currency": "BDT",
  "message": "Single day prediction successful",
  "confidence": "high"
}
```

### Multi-Day Forecast

```json
{
  "daily_forecast": [23429.77, 23674.21, 23469.89],
  "weekly_total": 164528.94,
  "monthly_total": 713311.11,
  "total_days": 30,
  "daily_statistics": {
    "min": 23429.77,
    "max": 23960.16,
    "mean": 23777.04,
    "std_dev": 184.32
  },
  "weekly_breakdown": [164528.94, 166169.26, 167481.46, 167323.66, 47807.8],
  "currency": "BDT",
  "message": "Forecast for 30 days completed successfully"
}
```

---

## Project Structure

```text
dr-seba-revenue-forecasting-system/
├── api/
│   ├── main.py
│   ├── models.py
│   ├── config.py
│   └── requirements.txt
├── ui/
│   ├── manage.py
│   ├── db.sqlite3
│   ├── requirements.txt
│   ├── forecaster/
│   ├── forecasting_ui/
│   ├── static/
│   └── templates/
├── models/
├── data/
├── tests/
├── RUN_TEAM_ACCESS.ps1
├── RUN_TEAM_ACCESS.bat
├── STOP_SERVERS.ps1
├── STOP_SERVERS.bat
└── README.md
```

---

## Technology Stack

| Area | Tools |
|------|-------|
| Backend API | FastAPI, Uvicorn, Pydantic |
| Frontend | Django, HTML, CSS |
| Machine Learning | CatBoost, NumPy, Pandas |
| Storage | SQLite |
| HTTP Integration | Requests |
| Runtime | Python 3.8+ |

---

## Local Setup

### Requirements

- Python 3.8 or later
- pip
- Git
- Windows, macOS, or Linux

### 1. Clone the repository

```bash
git clone https://github.com/mdzehadulislam8/drseba-revenue-forecasting-system.git
cd drseba-revenue-forecasting-system
```

### 2. Create a virtual environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
cd api
pip install -r requirements.txt
cd ..

cd ui
pip install -r requirements.txt
cd ..
```

---

## Run the Application

### Option 1: Automated startup

```powershell
.\RUN_TEAM_ACCESS.ps1
```

```cmd
RUN_TEAM_ACCESS.bat
```

### Option 2: Manual startup

Start the API server:

```bash
cd api
python main.py
```

Start the Django UI:

```bash
cd ui
python manage.py runserver 8001 --noreload
```

### Access points

| Service | URL | Purpose |
|---------|-----|---------|
| UI | http://localhost:8001 | Forecasting interface |
| API docs | http://localhost:8000/docs | Swagger UI |
| Health check | http://localhost:8000/health | API status |
| ReDoc | http://localhost:8000/redoc | Alternative API docs |

---

## Stop the Application

```powershell
.\STOP_SERVERS.ps1
```

```cmd
STOP_SERVERS.bat
```

If you started the services manually, stop them with `Ctrl+C` in each terminal.

---

## API Endpoints

### `POST /predict`

Returns a single revenue prediction for the submitted payload.

### `POST /forecast?days=30`

Returns a multi-day forecast with daily values and summary statistics.

### `GET /health`

Returns service status and model loading information.

---

## Testing

```bash
cd tests
python -m pytest -v
```

On Windows, use the project interpreter when possible:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

---

## Environment Variables

Optional `.env` file:

```env
DEBUG=True
DJANGO_SECRET_KEY=replace-me
API_BASE_URL=http://localhost:8000
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## Troubleshooting

| Issue | Likely Cause | Fix |
|-------|--------------|-----|
| Cannot connect to API | API server is not running | Start `api/main.py` |
| Port 8000 already in use | Another service is using the port | Stop the conflicting process |
| Port 8001 already in use | Another Django instance is active | Use a different port |
| Module not found | Dependencies are missing | Run `pip install -r requirements.txt` |
| Model load failed | Model file is missing or corrupted | Verify the `models/` folder |

---

## Security Notes

- Validate all input through Pydantic models.
- Keep secrets in environment variables.
- Restrict allowed hosts and CORS settings in production.
- Add authentication and rate limiting before public deployment.
- Use HTTPS in any non-local environment.

---

## Roadmap

- Add authenticated user access.
- Improve analytics and reporting views.
- Add export support for PDF and Excel.
- Introduce Docker and CI/CD workflows.
- Expand model monitoring and evaluation.

---

## Contact

For implementation support, model questions, or deployment guidance, contact the development team responsible for the Dr. Seba forecasting platform.

---

**Last updated:** April 15, 2026
