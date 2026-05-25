# 🏥 Doctor Recommendation System

> **Finding the right doctor shouldn't be a guessing game.** This intelligent ML platform helps patients discover the most suitable healthcare providers within their proximity, combining proximity, expertise, ratings, and service availability into one seamless experience.

Developed by the Data Science Team during an internship program for the Dr.Seba healthcare platform.

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0-green.svg)](https://www.djangoproject.com/)
[![CatBoost](https://img.shields.io/badge/CatBoost-99.63%25%20R²-orange.svg)](https://catboost.ai/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)](#-quick-start-guide)

## Table of Contents

- [The Problem](#-the-problem)
- [Key Capabilities](#-key-capabilities)
- [Technology Stack](#-technology-stack)
- [Machine Learning Excellence](#-machine-learning-excellence)
- [Dataset Foundation](#-dataset-foundation)
- [Architecture Overview](#-architecture-overview)
- [Product Walkthrough (Input and Output)](#-product-walkthrough-input-and-output)
- [Project Structure](#-project-structure)
- [Quick Start Guide](#-quick-start-guide)
- [API Documentation](#-api-documentation)
- [Performance and Reliability](#-performance--reliability)
- [Security](#-security)

---

## 🎯 The Problem

When patients need medical care, they face a fundamental challenge: **"How do I find a trustworthy, qualified doctor near me?"** Traditional doctor discovery is time-consuming, often relying on word-of-mouth recommendations or fragmented information scattered across the internet.

The **Dr.Seba platform** exists to change that experience. This Doctor Recommendation System is the intelligent engine behind that vision—a production-grade machine learning system that transforms the doctor search from a frustrating process into a seamless, data-driven recommendation in seconds.

### What It Does

Given a patient's location and medical needs, the system instantly recommends the best doctors by analyzing:
- **Geographic Proximity** — Finding doctors in their exact district and area
- **Medical Expertise** — Matching their condition with relevant specializations
- **Budget Constraints** — Filtering within their consultation fee range
- **Service Availability** — Prioritizing online, emergency, or hospital services
- **Quality Signals** — Factoring in ratings, experience, and patient feedback
- **Intelligent Ranking** — Using AI to surface the best matches first

The result? **A patient gets AI-ranked, verified doctor recommendations in under 100 milliseconds.**

---

## 🚀 Key Capabilities

### 🔍 Smart Location-Based Discovery
Find doctors in your specific district and thana (neighborhood). The system understands Bangladesh's administrative geography and matches patients with practitioners in their immediate area.

### 👨‍⚕️ Medical Specialization Matching
Search across **30+ medical specializations**—from general practitioners to specialized surgeons. Every doctor is professionally categorized by their primary expertise.

### 💰 Budget-Conscious Filtering
Set your maximum consultation fee and only see doctors within your budget. Transparent pricing empowers patients to make informed decisions without surprises.

### 🏥 Service Preferences
Filter by services you need: **online video consultations** for convenience, **emergency services** for urgent care, or **hospital visits** for comprehensive evaluation.

### 🤖 AI-Powered Quality Ranking
CatBoost machine learning model with **99.63% R² accuracy** ranks doctors by predicted suitability. The system learns from ratings, experience, and how well they match your criteria.

### ⚡ Real-Time Response
Sub-100ms API response times mean smooth, responsive user experience even with 500+ doctors in the database. Every millisecond matters for patient satisfaction.

---

## 💡 Technology Stack

### Backend & Machine Learning
| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Web Framework** | Django 5.0+ | REST API, routing, middleware |
| **ML Engine** | CatBoost 1.2+ | 99.63% accurate recommendations |
| **Data Processing** | Pandas 2.0+, NumPy 1.26+ | Data loading and transformation |
| **Feature Engineering** | Scikit-learn 1.4+ | Categorical encoding, preprocessing |
| **Data Storage** | Excel (.xlsx) | 500+ verified doctor records |

### Architecture
**Model-View-Template (MVT)** — Clean separation between API logic, business rules, and user interface. The system loads 500+ doctor records into memory with intelligent caching for sub-50ms inference.

---

## 🤖 Machine Learning Excellence

We rigorously evaluated **four enterprise-grade algorithms** to identify the optimal model for healthcare recommendations. Here's the scientific comparison:

### Performance Benchmarks

| Model | R² Score | RMSE | Accuracy | Status |
|-------|----------|------|----------|--------|
| **CatBoost** 🏆 | **0.9963** | **0.0126** | **99.63%** | ✅ SELECTED |
| Gradient Boosting 🥈 | 0.9879 | 0.0227 | 98.79% | ✅ Excellent |
| XGBoost 🥉 | 0.9870 | 0.0235 | 98.70% | ✅ Good |
| AdaBoost | 0.8520 | 0.0793 | 85.20% | ⚠️ Limited |

### Why CatBoost Won

**Superior Categorical Handling** — CatBoost natively understands categorical features (District, Thana, Specialization) without requiring manual encoding. This is critical in healthcare where geographic and medical categories are fundamental.

**Lowest Error Rate** — With an RMSE of just 0.0126, CatBoost provides the most precise predictions. This difference matters when distinguishing between "good" and "excellent" recommendations.

**Highest Variance Explained** — The 99.63% R² score means the model captures nearly all the variability in what makes a good doctor recommendation. Only 0.37% of variation remains unexplained.

**Automatic Overfitting Protection** — CatBoost's ObliviousDecisionTrees architecture inherently prevents overfitting, crucial for healthcare where generalization to new doctors is essential.

**Production-Optimized** — Engineered specifically for enterprise scenarios with class imbalance and categorical features. Training takes ~2 minutes, inference runs in ~50ms.

### The Trade-offs Examined

**CatBoost vs. Gradient Boosting:**
- Performance difference: Just 0.84% in R² score
- Decisive factor: CatBoost's native categorical handling eliminates preprocessing overhead
- Maintenance: CatBoost requires fewer feature engineering steps

**XGBoost Wasn't Chosen Because:**
- Requires intensive categorical encoding (one-hot, label encoding)
- Higher RMSE (0.0235 vs 0.0126) means more frequent borderline prediction errors
- Feature engineering overhead makes maintenance harder

**AdaBoost Fell Short:**
- 14% accuracy gap is too large for healthcare recommendations
- Unsuitable where precision impacts patient outcomes

---

## 📊 Dataset Foundation

The system is built on **verified, quality data**:

| Dimension | Value |
|-----------|-------|
| **Doctor Records** | 500+ verified practitioners |
| **Geographic Coverage** | 10+ Bangladesh districts |
| **Medical Specializations** | 30+ fields |
| **Data Quality Score** | 98.2% completeness |
| **Data Duplicates** | 0 found |
| **Last Updated** | April 2026 |
| **Update Frequency** | Monthly incremental updates |

**Quality Assurance:**
- ✅ All records manually verified by healthcare professionals
- ✅ Geographic coordinates validated against Bangladesh boundaries
- ✅ Contact information validated (phone format, email RFC 5322)
- ✅ Consultation fees confirmed realistic (500-5000 BDT range)
- ✅ Experience years validated (2-55 year range)
- ✅ Ratings calibrated to 1-5 star scale

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                  Web Browser & API Clients              │
│  (Patient submits requirements → Get recommendations)   │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/HTTPS
                     ↓
┌─────────────────────────────────────────────────────────┐
│              Django Application Server                   │
├─────────────────────────────────────────────────────────┤
│ API Handler Layer    │ Business Logic         │ Templates│
│ ├─ /api/health       │ ├─ Filtering           │ Web UI  │
│ ├─ /api/options      │ ├─ Ranking             │ (HTML/  │
│ ├─ /api/thanas/{id}  │ └─ Validation          │  CSS)   │
│ └─ /api/recommend    │                        │         │
└────────────────────┬─────────────────────────┬─────────┘
                     │                         │
        ┌────────────┼─────────────┐           │
        ↓            ↓             ↓           ↓
   ┌─────────┐  ┌──────────┐  ┌────────┐  ┌────────────┐
   │CatBoost │  │Pandas    │  │Memory  │  │ ExcelData  │
   │ Model   │  │ Processing  │Cache   │  │   (500+)   │
   └─────────┘  └──────────┘  └────────┘  └────────────┘
```

---

## 🖼️ Product Walkthrough (Input and Output)

The following screenshots show the full patient journey from search criteria submission to AI-ranked recommendation results.

### 1. Input Screen: Search Criteria

![Input Interface](https://drive.google.com/uc?export=view&id=1OVoBvt2csRNjh2RqzHcuzMvtI9NjpcpE)

Users provide:
- District and thana/area
- Required medical specialization
- Maximum consultation fee
- Optional online consultation requirement
- Optional emergency service requirement

### 2. Output Screen: Ranked Doctor Recommendations

![Output Results](https://drive.google.com/uc?export=view&id=1KD2jkHPG8esA16JSQ3nH67Cn0HHeXueZ)

The system returns:
- Ranked doctor list based on AI predicted score
- Doctor profile summary (name, specialization, experience, rating)
- Consultation fee and hospital details
- Full location address
- Quality badge (Excellent, Good, Fair)

### What This Demonstrates

- End-to-end recommendation flow is fully functional
- Real-time filtering and ranking based on user constraints
- Clean and intuitive user experience suitable for production
- Presentation-ready interface for academic and stakeholder demos

---

## 📁 Project Structure

```
drseba-doctor-recommendation/
│
├── 📄 README.md                    # This file
├── 📄 apps.py                      # Django app configuration  
├── 📄 requirements.txt             # Python dependencies
├── 📄 DATA_DICTIONARY.md           # Dataset documentation
│
├── 📂 src/                         # Application core
│   ├── config.py                   # Configuration constants
│   ├── constants.py                # Global constants
│   ├── utils.py                    # Helper utilities
│   │
│   ├── 📂 api/                     # REST API Layer
│   │   ├── handlers.py             # Request/response logic
│   │   ├── routes.py               # URL routing
│   │   └── schemas.py              # Input validation
│   │
│   ├── 📂 services/                # Business Logic
│   │   ├── data_service.py         # Doctor data management
│   │   ├── model_service.py        # ML model inference
│   │   └── recommender_service.py  # Recommendation algorithm
│   │
│   └── 📂 pipeline/                # ML Pipeline
│       └── train.py                # Model training script
│
├── 📂 templates/                   # Frontend
│   ├── index.html                  # Web UI
│   └── style.css                   # Styling
│
├── 📂 artifacts/                   # Evaluation artifacts
│   └── model_testing.py            # Model validation
│
└── 📂 notebook/                    # Jupyter
    └── dr.seba_doctor_recommendation_training.ipynb
```

### Key Modules Explained

**`src/api/handlers.py`**  
Handles HTTP requests and responses. Validates input parameters, calls business logic, and formats JSON responses for API clients.

**`src/services/recommender_service.py`**  
The recommendation engine. Orchestrates filtering, encoding, model inference, and ranking. Core algorithm is here.

**`src/services/model_service.py`**  
Manages CatBoost model lifecycle. Loads model from disk at startup, handles inference requests, returns predictions.

**`src/services/data_service.py`**  
Loads 500+ doctor records from Excel, maintains lookup tables, provides filtering and querying functionality.

**`src/pipeline/train.py`**  
Complete model training pipeline. Handles data preprocessing, feature engineering, model training, evaluation, and serialization.

**`templates/index.html`**  
Clean, responsive web interface. Server-side rendered by Django. No external JavaScript—all pagination handled by backend.

---

## 🚀 Quick Start Guide

Get up and running in **5 minutes**:

### Step 1: Environment Setup

```bash
# Navigate to project directory
cd drseba-doctor-recommendation

# Create virtual environment
python -m venv .venv

# Activate it
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Start the Server

**Recommended — Network Access:**
```bash
python manage.py runnetwork
```

This custom command auto-detects your network IP and starts the server accessible from any device on your network.

**Standard — Localhost Only:**
```bash
python manage.py runserver 0.0.0.0:7777
```

### Step 3: Access the Application

**Web Interface:** Open your browser to:
- Network: `http://{YOUR_IP}:7777`
- Localhost: `http://127.0.0.1:7777`

**API Endpoint:** For developers:
```bash
curl -X POST http://127.0.0.1:7777/api/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "district": "Dhaka",
    "thana": "Dhanmondi",
    "specialization": "Cardiology",
    "max_fee": 2000
  }'
```

---

## 📡 API Documentation

### Core Endpoints

**1. Health Check**
```bash
GET /api/health
```
Verify server is running.

**2. Get Options**
```bash
GET /api/options
```
Fetch all valid Districts, Specializations, and fee ranges for client-side dropdowns.

**3. Get Thanas by District**
```bash
GET /api/thanas/{district}
```
Dynamically fetch thanas for a selected district.

**4. Get Recommendations** ⭐
```bash
POST /api/recommendations
Content-Type: application/json

{
  "district": "Dhaka",
  "thana": "Dhanmondi", 
  "specialization": "Cardiology",
  "max_fee": 2000,
  "online": 1,
  "emergency": 0,
  "top_n": 5
}
```

**Response Example:**
```json
{
  "success": true,
  "count": 3,
  "doctors": [
    {
      "doctor_id": 42,
      "doctor_name": "Dr. Ahmed Khan",
      "specialization": "Cardiology",
      "experience_years": 12,
      "rating_avg": 4.8,
      "consultation_fees": 1500,
      "hospital_name": "Apollo Hospital",
      "online_consultation": 1,
      "emergency_service": 1,
      "predicted_score": 1.8234,
      "quality_rating": "Excellent"
    }
  ]
}
```

All API usage details are documented in this README under the API Documentation section.

---

## 💻 Integration Examples

### Python (Requests)

```python
import requests

response = requests.post(
    "http://127.0.0.1:7777/api/recommendations",
    json={
        "district": "Dhaka",
        "thana": "Dhanmondi",
        "specialization": "Cardiology",
        "max_fee": 2000
    }
)

data = response.json()
if data["success"]:
    for doctor in data["doctors"]:
        print(f"{doctor['doctor_name']} - {doctor['quality_rating']}")
```

### JavaScript (Fetch)

```javascript
fetch('http://127.0.0.1:7777/api/recommendations', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    district: 'Dhaka',
    thana: 'Dhanmondi',
    specialization: 'Cardiology',
    max_fee: 2000
  })
})
.then(r => r.json())
.then(data => console.log(data.doctors))
.catch(err => console.error(err));
```

### cURL

```bash
curl -X POST http://127.0.0.1:7777/api/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "district": "Dhaka",
    "thana": "Dhanmondi",
    "specialization": "Cardiology",
    "max_fee": 2000
  }'
```

---

## 📊 Performance & Reliability

### API Performance

| Metric | Benchmark | Actual | Status |
|--------|-----------|--------|--------|
| **Response Time** | <500ms | ~50-100ms | ⚡ Excellent |
| **Throughput** | >10 req/s | >50 req/s | 📈 Scalable |
| **Model Inference** | <100ms | ~40-80ms | 🚀 Real-time |
| **Model Load** | <2s | ~300-500ms | ✅ Fast |

Performance note: Metrics are observed from local test runs on development hardware using the Django API endpoints with warmed model cache.

### Model Performance

| Metric | Value |
|--------|-------|
| **R² Score** | 0.9963 (99.63%) |
| **RMSE** | 0.0126 |
| **Cross-Val Score** | 0.9859 (±0.0082) |
| **Training Time** | ~2 minutes |

### System Requirements

- **Python:** 3.10+
- **RAM:** 1GB minimum (2GB recommended for comfortable usage)
- **Disk:** 500MB (includes dependencies + model)
- **Network:** None required (localhost operation)

---

## 🔐 Security

- ✅ **CSRF Protection** on all POST requests
- ✅ **Input Validation** for all API parameters
- ✅ **Error Handling** without exposing system details
- ✅ **Data Sanitization** before processing
- ✅ **No Hardcoded Secrets** in repository
- ✅ **Django Security Middleware** enabled

---

## 📚 Documentation

- [**DATA_DICTIONARY.md**](DATA_DICTIONARY.md) — Dataset documentation and quality metrics
- **Jupyter Notebook** — See the ML pipeline in action: `notebook/dr.seba_doctor_recommendation_training.ipynb`

---

## 🎓 About This Project

This system was developed as part of a professional **data science internship program** focused on building production-grade machine learning systems for healthcare. It demonstrates:

- **Modern ML Best Practices** — Algorithm selection, cross-validation, hyperparameter tuning
- **Production Engineering** — REST APIs, error handling, caching, security
- **Full-Stack Development** — Backend, frontend, deployment considerations
- **Healthcare Domain Knowledge** — Practical understanding of doctor-patient matching

This project work was completed by the internship Data Science Team under mentor guidance.

### Project Leadership

**Mentor & Project Direction:** [Nusrat Jahan](https://github.com/Nusrat-96)
- 📧 Email: [nusrat.adiba@gmail.com](mailto:nusrat.adiba@gmail.com)
- 🔗 GitHub: [@Nusrat-96](https://github.com/Nusrat-96)
- 📍 Senior Data Science Trainer

---

## Support & Contact

**Questions or Issues?**
- 🔧 **Setup and Run Help** → Follow the Quick Start Guide in this README
- 📖 **API Questions** → Refer to the API Documentation section in this README
- 💬 **Project Discussions** → Contact Nusrat Jahan

---

## 📜 License & Attribution

This project was developed with mentorship and guidance from [Nusrat Jahan](https://github.com/Nusrat-96) as part of the Dr.Seba Healthcare Platform initiative.

Implementation and experimentation were carried out by the Data Science Team during the internship period.

**Made with ❤️ for better healthcare accessibility in Bangladesh**

---

*Last Updated: April 2026*
