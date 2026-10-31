"""State Schema for Underwriting Agent."""

from typing import Any, Dict, List, TypedDict


class UnderwritingState(TypedDict):
    # Raw Applicant Inputs
    applicant_data: Dict[str, Any]

    # External Live API Enrichments
    geo_data: Dict[str, Any]
    benchmark_rate_monthly: float

    # Actuarial Calculations & Surcharges
    pricing_data: Dict[str, Any]

    # Grounding & Citations
    retrieved_clauses: List[str]

    # High-Risk What-If Scenarios
    counterfactual_scenarios: Dict[str, Any]

    # Final Generated Output
    final_synthesis: str