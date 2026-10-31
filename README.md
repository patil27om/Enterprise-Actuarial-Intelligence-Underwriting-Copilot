# Insurance Actuarial & Underwriting Copilot

A small end-to-end project I put together to experiment with agentic workflows in regulated pricing. It calculates individual health insurance quotes based on Affordable Care Act (Title 45 CFR § 147.102) rating rules, checks public CMS benchmarks, and uses an LLM to generate plain-English explanations with actionable steps to lower premiums.

I specifically wanted to avoid two common issues I see with AI demos:
1. **Black-box pricing:** Surcharges and age curves are never left to the LLM to guess. All calculations are deterministic Python code.
2. **Expensive infrastructure:** Vector lookups run locally using ChromaDB and a CPU-friendly Hugging Face model (`all-MiniLM-L6-v2`), keeping token usage focused on final synthesis.

---

## What It Does

- **Deterministic ACA Calculations:** Implements standard 3:1 age curves, the statutory 45% tobacco surcharge, metabolic BMI adjustments, and family tiering (capping chargeable kids at 3).
- **Public Data Lookups:** Resolves US postal ZIP codes to rating territories using the free Zippopotam API and compares quotes against state Silver Plan benchmark rates from CMS open datasets.
- **Agent Workflow (LangGraph):** Routes applicant state through enrichment, deterministic pricing, conditional logic (triggering a counterfactual savings node only if surcharges exist), and policy retrieval.
- **Explainable Audits:** Uses GPT-6 Luna to write a breakdown of how the numbers were calculated and what steps (like a 90-day cessation program) would reduce costs.
- **Interactive UI:** A simple Streamlit dashboard for adjusting inputs and reviewing results side-by-side.

---

## Architecture Diagram

1. User Inputs Data (Streamlit UI)
The user enters applicant details in the browser (age, ZIP code, BMI, smoking status, and dependents). Clicking "Evaluate" sends this information as a JSON payload to the FastAPI backend.

2. Validation & Entry (FastAPI Gateway)
FastAPI receives the request and checks the data format using Pydantic. If any field is invalid (like a 3-digit ZIP or negative age), it immediately returns an error. If valid, it hands the request off to the processing pipeline.

3. Data Enrichment (External APIs)
Before calculating any prices, the system gathers external context:

It calls a free postal service to turn the 5-digit ZIP code into a city, state, and geographic rating area.

It pulls the official baseline health insurance rate for that specific state using public CMS benchmark data.

4. Math Calculation (Actuarial Engine)
All pricing math happens strictly in Python code, not in the AI:

It applies the federal 3:1 age curve factor to the base rate.

It calculates legal surcharges, including tobacco use (45%), elevated BMI, and family dependent allowances.

It totals the base rate and surcharges to produce the exact monthly and annual premium figures.

5. Workflow Coordination (LangGraph)
A state machine manages the decision flow:

Decision check: If the applicant has risk surcharges, the system routes to a savings node that calculates the exact dollars saved if they change habits (like quitting smoking or lowering BMI). If they have no surcharges, it skips this step.

Document search: The system looks up relevant health insurance regulations in a local ChromaDB database stored directly on your computer, running at zero cost.

AI synthesis: GPT-6 Luna receives the calculated numbers, the policy rules, and the savings paths. It writes a clear, audit-style breakdown explaining how the price was determined.

6. Displaying Results (Return to UI)
FastAPI bundles the calculated numbers, savings estimates, and AI explanation into a single response. The Streamlit screen updates instantly to display the metrics, cost breakdown, and savings recommendations side-by-side.


### 🧪 Automated Testing

The repository includes a complete test suite covering deterministic calculations, MCP integrations, LangGraph routing, and FastAPI schema validation:

pytest -v

All 11 test cases pass in ~1.2s:

tests/test_actuarial_math.py::test_aca_age_factor_boundaries PASSED         [  9%]
tests/test_actuarial_math.py::test_tobacco_surcharge_application PASSED     [ 18%]
tests/test_actuarial_math.py::test_metabolic_bmi_surcharge PASSED           [ 27%]
tests/test_actuarial_math.py::test_dependent_charge_cap PASSED              [ 36%]
tests/test_api_endpoints.py::test_health_check_endpoint PASSED              [ 45%]
tests/test_api_endpoints.py::test_quote_endpoint_validation_error PASSED    [ 54%]
tests/test_graph_state.py::test_conditional_router_identifies_risk PASSED   [ 63%]
tests/test_graph_state.py::test_counterfactual_engine_math PASSED           [ 72%]
tests/test_mcp_services.py::test_resolve_valid_zipcode PASSED               [ 81%]
tests/test_mcp_services.py::test_resolve_invalid_zipcode_fallback PASSED     [ 90%]
tests/test_mcp_services.py::test_cms_benchmark_lookup PASSED                [100%]

---

### 📡 Sample API Request & Response

#### Request (POST /api/v1/quote)

curl -X POST "http://localhost:8000/api/v1/quote" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 45,
    "gender": "male",
    "bmi": 29.5,
    "bloodpressure": 125,
    "diabetic": "No",
    "children": 2,
    "smoker": "Yes",
    "zipcode": "33101"
  }'

#### Response Payload

{
  "location": {
    "zipcode": "33101",
    "city": "Miami",
    "state": "Florida",
    "state_code": "FL",
    "region": "southeast",
    "status": "resolved"
  },
  "benchmark_rate_monthly": 480.0,
  "pricing": {
    "final_annual_premium": 19982.83,
    "final_monthly_premium": 1665.24,
    "breakdown": {
      "base_annual_premium": 12188.16,
      "age_factor": 2.116,
      "tobacco_surcharge": 5484.67,
      "bmi_surcharge": 810.0,
      "hypertension_surcharge": 0.0,
      "dependents_surcharge": 1500.0,
      "chargeable_children": 2
    }
  },
  "counterfactual_scenarios": {
    "tobacco_cessation": {
      "action": "Enroll in an approved 90-day Tobacco Cessation Program (Title 45 CFR § 147.102)",
      "annual_savings_usd": 5484.67,
      "monthly_savings_usd": 457.06,
      "revised_annual_premium": 14498.16
    },
    "bmi_normalization": {
      "action": "Maintain documented participation in certified wellness program reaching BMI < 25.0",
      "annual_savings_usd": 810.0,
      "monthly_savings_usd": 67.5,
      "revised_annual_premium": 19172.83
    }
  },
  "underwriting_synthesis": "## 1. Executive Underwriting Summary\n\nThe stated quote is **$1,665.24 per month ($19,982.83 annually)**. The calculation reconciles arithmetically..."
}

---

### ⚖️ License & Disclaimer

Distributed under the **MIT License**. The calculations and regulatory rules simulated in this project reflect statutory frameworks under Title 45 CFR and public CMS dataset benchmarks. It is designed for demonstration and architectural portfolio purposes and does not represent binding insurance underwriting advice.