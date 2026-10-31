"""Unit tests for deterministic actuarial calculations."""

import pytest
from app.mcp_servers.actuarial_calc_mcp import (
    compute_aca_age_factor,
    calculate_actuarial_quote,
)


def test_aca_age_factor_boundaries():
    """Verifies statutory ACA age curve boundary limits."""
    assert compute_aca_age_factor(19) == 0.635
    assert compute_aca_age_factor(20) == 0.635
    assert compute_aca_age_factor(21) == 1.000
    assert compute_aca_age_factor(64) == 3.000
    assert compute_aca_age_factor(75) == 3.000

    mid_factor = compute_aca_age_factor(42.5)
    assert 1.99 <= mid_factor <= 2.01


def test_tobacco_surcharge_application():
    """Verifies standard 45% tobacco surcharge calculation."""
    monthly_base = 500.0

    non_smoker_quote = calculate_actuarial_quote(
        age=21, bmi=22.0, smoker="No", children=0, monthly_benchmark=monthly_base
    )
    smoker_quote = calculate_actuarial_quote(
        age=21, bmi=22.0, smoker="Yes", children=0, monthly_benchmark=monthly_base
    )

    base_annual = 6000.0
    expected_surcharge = round(base_annual * 0.45, 2)

    assert non_smoker_quote["breakdown"]["tobacco_surcharge"] == 0.0
    assert smoker_quote["breakdown"]["tobacco_surcharge"] == expected_surcharge
    assert smoker_quote["final_annual_premium"] == base_annual + expected_surcharge


def test_metabolic_bmi_surcharge():
    """Verifies $180/unit surcharge for BMI > 25.0."""
    monthly_base = 400.0

    quote_normal = calculate_actuarial_quote(
        age=21, bmi=24.0, smoker="No", children=0, monthly_benchmark=monthly_base
    )
    assert quote_normal["breakdown"]["bmi_surcharge"] == 0.0

    quote_overweight = calculate_actuarial_quote(
        age=21, bmi=29.5, smoker="No", children=0, monthly_benchmark=monthly_base
    )
    assert quote_overweight["breakdown"]["bmi_surcharge"] == 810.00


def test_dependent_charge_cap():
    """Verifies that dependent charges cap at 3 children per federal rules."""
    monthly_base = 400.0

    quote_2_kids = calculate_actuarial_quote(
        age=30, bmi=22.0, smoker="No", children=2, monthly_benchmark=monthly_base
    )
    assert quote_2_kids["breakdown"]["chargeable_children"] == 2
    assert quote_2_kids["breakdown"]["dependents_surcharge"] == 1500.00

    quote_5_kids = calculate_actuarial_quote(
        age=30, bmi=22.0, smoker="No", children=5, monthly_benchmark=monthly_base
    )
    assert quote_5_kids["breakdown"]["chargeable_children"] == 3
    assert quote_5_kids["breakdown"]["dependents_surcharge"] == 2250.00