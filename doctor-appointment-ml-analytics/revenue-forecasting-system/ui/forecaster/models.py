"""
Models for forecaster app
"""
from django.db import models


class ForecastRecord(models.Model):
    """Stores forecast request/response records"""
    
    total_bookings = models.IntegerField()
    avg_fee = models.FloatField()
    commission_rate = models.FloatField()
    experience_years = models.IntegerField()
    rating_avg = models.FloatField()
    
    district = models.CharField(max_length=100)
    specialization_group = models.CharField(max_length=100)
    hospital_type = models.CharField(max_length=100)
    
    lag_1 = models.FloatField()
    lag_7 = models.FloatField()
    rolling_mean_7 = models.FloatField()
    
    prediction = models.FloatField(null=True, blank=True)
    forecast_days = models.IntegerField(default=30)
    forecast_total = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Forecast Records"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Forecast - {self.district} - {self.created_at}"
