"""Actuarial Pricing Engine.

Implements ACA statutory rating rules, age curves, and clinical risk adjustments.
"""


def compute_aca_age_factor(age: float) -> float:
    """Computes the federal ACA 3:1 age-rating factor.

    - Under 21: Child discount factor (0.635)
    - Age 21: Benchmark standard (1.000)
    - Ages 21-64: Scales monotonically from 1.000 to 3.000
    - Age 64+: Capped at statutory maximum (3.000)
    """
    if age < 21:
        return 0.635
    if age >= 64:
        return 3.000
    # Linear progression along 43-year adult band
    return round(1.000 + ((age - 21.0) / 43.0) * 2.000, 3)


def calculate_actuarial_quote(
    age: float,
    bmi: float,
    smoker: str,
    children: int,
    monthly_benchmark: float,
    bloodpressure: int = 120,
) -> dict:
    """Calculates actuarial premium and returns an itemized audit breakdown."""
    age_factor = compute_aca_age_factor(age)
    base_annual = monthly_benchmark * 12.0 * age_factor

    # 1. Tobacco Surcharge (45% on age-adjusted base per underwriting manual)
    is_smoker = str(smoker).strip().lower() in ["yes", "true", "1", "y"]
    tobacco_surcharge = round(base_annual * 0.45, 2) if is_smoker else 0.0

    # 2. Metabolic Surcharge (Obesity loading: $180/unit above BMI 25.0)
    bmi_surcharge = 0.0
    if bmi > 25.0:
        excess_bmi = bmi - 25.0
        bmi_surcharge = round(excess_bmi * 180.0, 2)

    # 3. Clinical Hypertension Surcharge (Systolic >= 140 mmHg incurs flat cardiovascular loading)
    hypertension_surcharge = 450.0 if bloodpressure >= 140 else 0.0

    # 4. Dependent Tiering (ACA rule: charge up to 3 oldest children under 21 at $750/child)
    chargeable_children = min(max(0, int(children)), 3)
    dependents_surcharge = round(chargeable_children * 750.0, 2)

    # Total composite calculation
    total_annual = round(
        base_annual + tobacco_surcharge + bmi_surcharge + hypertension_surcharge + dependents_surcharge,
        2,
    )
    total_monthly = round(total_annual / 12.0, 2)

    return {
        "final_annual_premium": total_annual,
        "final_monthly_premium": total_monthly,
        "breakdown": {
            "base_annual_premium": round(base_annual, 2),
            "age_factor": age_factor,
            "tobacco_surcharge": tobacco_surcharge,
            "bmi_surcharge": bmi_surcharge,
            "hypertension_surcharge": hypertension_surcharge,
            "dependents_surcharge": dependents_surcharge,
            "chargeable_children": chargeable_children,
        },
    }