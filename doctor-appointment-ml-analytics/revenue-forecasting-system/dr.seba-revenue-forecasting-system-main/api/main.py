"""
Commission Revenue Forecasting FastAPI
Provides REST API endpoints for commission revenue predictions
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import logging
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.test_model import CommissionForecaster
from api.models import PredictionRequest, PredictionResponse, ForecastResponse
from api.config import MODEL_PATH, API_VERSION

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Commission Revenue Forecasting API",
    description="API for predicting commission revenue with daily, weekly, and monthly forecasts",
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize forecaster (global instance)
try:
    forecaster = CommissionForecaster(MODEL_PATH)
    logger.info(f"✓ Forecaster initialized with model from {MODEL_PATH}")
except Exception as e:
    logger.error(f"Failed to initialize forecaster: {e}")
    forecaster = None


@app.get("/")
def read_root():
    """API root endpoint with service information."""
    return {
        "service": "Commission Revenue Forecasting API",
        "version": API_VERSION,
        "status": "operational" if forecaster else "error",
        "endpoints": {
            "predict": "/predict",
            "forecast": "/forecast",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    if forecaster is None:
        raise HTTPException(status_code=503, detail="Forecaster not initialized")
    return {
        "status": "healthy",
        "model_loaded": True,
        "service": "Commission Revenue Forecasting API"
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    """
    Get single day commission revenue prediction.
    
    Args:
        request: Input data with commissioner details
        
    Returns:
        PredictionResponse: Predicted commission revenue for next day
    """
    if forecaster is None:
        raise HTTPException(status_code=503, detail="Forecaster not initialized")
    
    try:
        # Convert request to dictionary
        user_data = request.dict()
        
        # Generate 1-day forecast
        forecast = forecaster.forecast(user_data, days=1)
        
        return PredictionResponse(
            prediction=round(forecast[0], 2),
            currency="BDT",
            message="Single day prediction successful"
        )
    except ValueError as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in prediction: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/forecast", response_model=ForecastResponse)
def forecast(request: PredictionRequest, days: int = 30):
    """
    Get multi-day commission revenue forecast with daily, weekly, monthly summaries.
    
    Args:
        request: Input data with commissioner details
        days: Number of days to forecast (default: 30, range: 1-365)
        
    Returns:
        ForecastResponse: Detailed forecast with statistics, daily/weekly/monthly summaries
    """
    if forecaster is None:
        raise HTTPException(status_code=503, detail="Forecaster not initialized")
    
    # Validate days parameter
    if days < 1 or days > 365:
        raise HTTPException(status_code=400, detail="Days must be between 1 and 365")
    
    try:
        # Convert request to dictionary
        user_data = request.dict()
        
        # Generate forecast
        predictions = forecaster.forecast(user_data, days=days)
        
        # Calculate summaries
        daily_forecast = [round(p, 2) for p in predictions[:7]]  # First 7 days
        weekly_total = round(sum(predictions[:7]), 2)
        monthly_total = round(sum(predictions), 2)
        
        # Calculate statistics
        min_daily = round(min(predictions), 2)
        max_daily = round(max(predictions), 2)
        mean_daily = round(sum(predictions) / len(predictions), 2)
        
        import numpy as np
        std_daily = round(float(np.std(predictions)), 2)
        
        # Weekly breakdown
        weekly_breakdown = []
        for i in range(0, len(predictions), 7):
            week_sum = round(sum(predictions[i:i+7]), 2)
            weekly_breakdown.append(week_sum)
        
        return ForecastResponse(
            daily_forecast=daily_forecast,
            weekly_total=weekly_total,
            monthly_total=monthly_total,
            total_days=days,
            daily_statistics={
                "min": min_daily,
                "max": max_daily,
                "mean": mean_daily,
                "std_dev": std_daily
            },
            weekly_breakdown=weekly_breakdown,
            currency="BDT",
            message=f"Forecast for {days} days completed successfully"
        )
    except ValueError as e:
        logger.error(f"Forecast error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in forecast: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
