"""CMS Benchmark Rate Provider.

Provides state-level benchmark Qualified Health Plan (QHP) monthly baseline rates.
"""

# Average monthly benchmark rates (Silver Level) based on CMS open data
CMS_STATE_BENCHMARKS = {
    "AK": 820.0,
    "WY": 740.0,
    "NY": 690.0,
    "NJ": 580.0,
    "NC": 530.0,
    "CA": 520.0,
    "GA": 505.0,
    "FL": 480.0,
    "TX": 465.0,
    "PA": 475.0,
    "OH": 440.0,
    "UT": 410.0,
    "DEFAULT": 490.0,
}


def get_state_benchmark(state_code: str) -> dict:
    """Returns the baseline monthly Silver Plan benchmark for a given state code."""
    code = state_code.upper().strip()
    rate = CMS_STATE_BENCHMARKS.get(code, CMS_STATE_BENCHMARKS["DEFAULT"])
    return {
        "state_code": code,
        "monthly_benchmark_usd": rate,
        "annual_benchmark_usd": round(rate * 12.0, 2),
        "source": "CMS Qualified Health Plan (QHP) Open Benchmark Index",
    }