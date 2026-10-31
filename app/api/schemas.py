"""Pydantic Request and Response Schemas."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class QuoteRequest(BaseModel):
    """Applicant details submitted by the insurance agent."""

    age: float = Field(..., ge=18, le=100, description="Applicant age in years (18-100)")
    gender: str = Field(default="male", description="Biological gender ('male' or 'female')")
    bmi: float = Field(..., ge=12.0, le=60.0, description="Body Mass Index (12.0-60.0)")
    bloodpressure: int = Field(default=120, ge=70, le=240, description="Systolic resting blood pressure (mmHg)")
    diabetic: str = Field(default="No", description="'Yes' or 'No'")
    children: int = Field(default=0, ge=0, le=10, description="Number of child dependents")
    smoker: str = Field(..., description="Tobacco user ('Yes' or 'No')")
    zipcode: str = Field(..., min_length=5, max_length=5, pattern=r"^\d{5}$", description="5-digit US postal ZIP code")

    model_config = {
        "json_schema_extra": {
            "example": {
                "age": 45,
                "gender": "male",
                "bmi": 29.5,
                "bloodpressure": 125,
                "diabetic": "No",
                "children": 2,
                "smoker": "Yes",
                "zipcode": "33101",
            }
        }
    }


class PricingBreakdown(BaseModel):
    base_annual_premium: float
    age_factor: float
    tobacco_surcharge: float
    bmi_surcharge: float
    hypertension_surcharge: float
    dependents_surcharge: float
    chargeable_children: int


class PricingSummary(BaseModel):
    final_annual_premium: float
    final_monthly_premium: float
    breakdown: PricingBreakdown


class GeoResolution(BaseModel):
    zipcode: str
    city: str
    state: str
    state_code: str
    region: str
    status: str


class QuoteResponse(BaseModel):
    """Full actuarial quote and audit report."""

    location: GeoResolution
    benchmark_rate_monthly: float
    pricing: PricingSummary
    retrieved_clauses_count: int
    counterfactual_scenarios: Dict[str, Any]
    underwriting_synthesis: str