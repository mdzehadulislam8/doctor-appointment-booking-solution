# Healthcare ML Analytics & BI Platform 🧠📈

This directory houses the data intelligence core of the **Doctor Appointment Booking Solution**. It is divided into three main modules focused on Machine Learning, Business Intelligence, and Predictive Analytics to provide a data-driven approach to healthcare management.

## 📁 Modules Overview

### 1. Doctor Recommendation ML Platform (`doctor-recommendation-ml-platform`)
An intelligent recommendation engine built to assist patients in finding the most suitable doctors.
*   **Purpose**: Matches patients with specialists based on symptoms, past medical history, and doctor ratings.
*   **Tech Stack**: Python, Scikit-learn, Pandas, FastAPI/Flask (for serving).
*   **Key Files**: Model training notebooks, serialized model artifacts, and API source code.

### 2. Revenue Forecasting System (`revenue-forecasting-system`)
A time-series forecasting model designed for hospital administrators and stakeholders to predict financial inflows.
*   **Purpose**: Analyzes historical appointment and payment data to project future revenue. Helps in financial planning and resource allocation.
*   **Tech Stack**: Python, Statsmodels (ARIMA/Prophet), Pandas, Jupyter Notebooks.
*   **Key Files**: `api/`, `models/`, `data/`, and evaluation `tests/`.

### 3. Power BI Analytics Dashboard (`power-bi -analytics-dashboard-for-healthcare-platform`)
Interactive business intelligence dashboards providing a macroscopic view of the hospital's operations.
*   **Purpose**: Visualizes key metrics such as ICU/Ward bed availability, appointment volume trends, demographic distribution of patients, and revenue split.
*   **Tech Stack**: Microsoft Power BI, DAX, Power Query.

## 🚀 Setup & Installation

To run the machine learning servers locally:

1. Navigate to the specific ML project directory:
   ```bash
   cd doctor-recommendation-ml-platform
   # OR
   # cd revenue-forecasting-system
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   ```

3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Explore the `notebooks/` directory to see model training details, or look at the respective `README.md` files inside each sub-directory for detailed API execution commands.

## 💡 Impact
By integrating these systems, the healthcare platform transforms from a simple booking tool into an **Intelligent Healthcare System** that optimizes hospital resources, maximizes revenue, and significantly improves the patient experience.
