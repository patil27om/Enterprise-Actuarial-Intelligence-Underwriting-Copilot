"""Tests for LangGraph conditional branching and counterfactual generation."""

import pytest
from app.graph.workflow import condition_check_surcharges
from app.graph.nodes import node_compute_counterfactuals


def test_conditional_router_identifies_risk():
    """Verifies that profiles with surcharges route to counterfactuals."""
    high_risk_state = {
        "pricing_data": {
            "breakdown": {
                "tobacco_surcharge": 5484.67,
                "bmi_surcharge": 0.0,
                "hypertension_surcharge": 0.0,
            }
        }
    }
    assert (
        condition_check_surcharges(high_risk_state)
        == "node_compute_counterfactuals"
    )

    standard_risk_state = {
        "pricing_data": {
            "breakdown": {
                "tobacco_surcharge": 0.0,
                "bmi_surcharge": 0.0,
                "hypertension_surcharge": 0.0,
            }
        }
    }
    assert (
        condition_check_surcharges(standard_risk_state)
        == "node_retrieve_policies"
    )


def test_counterfactual_engine_math():
    """Verifies that counterfactual reduction paths subtract exact surcharge amounts."""
    mock_state = {
        "pricing_data": {
            "final_annual_premium": 19982.83,
            "breakdown": {
                "tobacco_surcharge": 5484.67,
                "bmi_surcharge": 810.00,
            },
        }
    }

    result = node_compute_counterfactuals(mock_state)
    scenarios = result["counterfactual_scenarios"]

    assert "tobacco_cessation" in scenarios
    assert scenarios["tobacco_cessation"]["annual_savings_usd"] == 5484.67
    assert scenarios["tobacco_cessation"]["revised_annual_premium"] == round(
        19982.83 - 5484.67, 2
    )

    assert "bmi_normalization" in scenarios
    assert scenarios["bmi_normalization"]["annual_savings_usd"] == 810.00
    assert scenarios["bmi_normalization"]["revised_annual_premium"] == round(
        19982.83 - 810.00, 2
    )