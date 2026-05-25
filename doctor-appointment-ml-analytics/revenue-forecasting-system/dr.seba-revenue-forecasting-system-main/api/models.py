"""
Pydantic models for API request/response validation
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional


class PredictionRequest(BaseModel):
    """Request model for predictions."""
    
    total_bookings: int = Field(..., description="Total number of bookings", ge=0)
    avg_fee: float = Field(..., description="Average consultation fee", gt=0)
    commission_rate: float = Field(..., description="Commission rate (0-1)", ge=0, le=1)
    service_charge: float = Field(..., description="Service charge per booking", ge=0)
    experience_years: int = Field(..., description="Years of professional experience", ge=0)
    rating_avg: float = Field(..., description="Average rating (0-5)", ge=0, le=5)
    
    district: str = Field(..., description="Geographic district")
    specialization_group: str = Field(..., description="Medical specialization")
    hospital_type: str = Field(..., description="Type of hospital/clinic")
    
    lag_1: float = Field(..., description="Previous day commission revenue", gt=0)
    lag_7: float = Field(..., description="7-day lagged revenue", gt=0)
    rolling_mean_7: float = Field(..., description="7-day rolling mean revenue", gt=0)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_bookings": 180,
                "avg_fee": 700,
                "commission_rate": 0.12,
                "service_charge": 60,
                "experience_years": 12,
                "rating_avg": 4.7,
                "district": "Chattogram",
                "specialization_group": "Neurologist",
                "hospital_type": "Private Hospital",
                "lag_1": 9500,
                "lag_7": 8800,
                "rolling_mean_7": 9000
            }
        }
    )


class PredictionResponse(BaseModel):
    """Response model for single prediction."""
    
    prediction: float = Field(..., description="Predicted commission revenue")
    currency: str = Field(default="BDT", description="Currency code")
    message: str = Field(..., description="Response message")


class DailyStatistics(BaseModel):
    """Daily forecast statistics."""
    
    min: float = Field(..., description="Minimum daily prediction")
    max: float = Field(..., description="Maximum daily prediction")
    mean: float = Field(..., description="Mean daily prediction")
    std_dev: float = Field(..., description="Standard deviation of predictions")


class ForecastResponse(BaseModel):
    """Response model for multi-day forecast."""
    
    daily_forecast: List[float] = Field(..., description="Daily predictions for first 7 days")
    weekly_total: float = Field(..., description="Total prediction for first week")
    monthly_total: float = Field(..., description="Total prediction for entire period")
    total_days: int = Field(..., description="Total days in forecast")
    
    daily_statistics: DailyStatistics = Field(..., description="Statistics of predictions")
    weekly_breakdown: List[float] = Field(..., description="Weekly totals breakdown")
    
    currency: str = Field(default="BDT", description="Currency code")
    message: str = Field(..., description="Response message")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
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
        }
    )
