"""
Enterprise Insurance Underwriting & Copilot Interface.
Streamlit Agent Dashboard consuming the FastAPI / LangGraph backend.
"""

import os
import httpx
import streamlit as st

# Configure page settings
st.set_page_config(
    page_title="Agent Underwriting Copilot",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling for enterprise dashboard
st.markdown(
    """
    <style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 16px;
        border-left: 5px solid #1E88E5;
    }
    .savings-card {
        background-color: #e8f5e9;
        border-radius: 8px;
        padding: 14px;
        border: 1px solid #c8e6c9;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🛡️ Enterprise Underwriting & Actuarial Intelligence Copilot")
st.caption(
    "Automated Geocoding & CMS Benchmarks • ACA Rating Curve Engine • LangGraph State Machine • GPT-6 Luna Explainer"
)

# Determine default API URL:
# If running inside Docker Compose, it defaults to the Docker network name 'http://api:8000/api/v1/quote'
# If running locally on Mac/PC, it defaults to 'http://localhost:8000/api/v1/quote'
DEFAULT_API_URL = os.getenv("API_URL", "http://api:8000/api/v1/quote")

# Sidebar: Applicant Information Form
with st.sidebar:
    st.header("📋 Applicant Profile")
    zipcode = st.text_input("US Postal ZIP Code", value="33101", max_chars=5)
    age = st.number_input("Applicant Age", min_value=18, max_value=99, value=45, step=1)
    gender = st.selectbox("Biological Sex", ["male", "female"])
    bmi = st.number_input(
        "Body Mass Index (BMI)", min_value=12.0, max_value=60.0, value=29.5, step=0.1
    )
    smoker = st.selectbox("Tobacco User (Past 6 Months)?", ["Yes", "No"])
    children = st.slider("Eligible Dependents (< Age 26)", 0, 8, 2)
    bloodpressure = st.number_input(
        "Resting Systolic Blood Pressure (mmHg)", min_value=70, max_value=220, value=125, step=1
    )
    diabetic = st.selectbox("Diagnosed Diabetic?", ["No", "Yes"])

    api_endpoint = st.text_input("FastAPI Endpoint", value=DEFAULT_API_URL)
    submit_btn = st.button("Evaluate Application & Calculate Quote", type="primary", use_container_width=True)

# Main Dashboard Execution
if submit_btn:
    # Normalize the endpoint URL automatically to prevent 404/405 errors
    target_url = api_endpoint.strip().rstrip("/")
    if not target_url.endswith("/api/v1/quote"):
        target_url = f"{target_url}/api/v1/quote"

    payload = {
        "age": float(age),
        "gender": gender,
        "bmi": float(bmi),
        "bloodpressure": int(bloodpressure),
        "diabetic": diabetic,
        "children": int(children),
        "smoker": smoker,
        "zipcode": str(zipcode).strip(),
    }

    with st.spinner("Executing LangGraph State Machine: Resolving Geo, Fetching CMS Baseline, & Querying GPT-6 Luna..."):
        try:
            with httpx.Client(timeout=60.0) as client:
                res = client.post(target_url, json=payload)

            if res.status_code == 200:
                data = res.json()
                loc = data["location"]
                pricing = data["pricing"]
                breakdown = pricing["breakdown"]
                cms_benchmark = data["benchmark_rate_monthly"]
                counterfactuals = data["counterfactual_scenarios"]
                synthesis = data["underwriting_synthesis"]

                # 1. Geolocation & Rating Area Banner
                st.success(
                    f"📍 **Rating Territory Identified:** {loc['city']}, {loc['state']} ({loc['state_code']}) — "
                    f"Rating Region: `{loc['region'].upper()}` | Status: `{loc['status'].upper()}`"
                )

                # 2. Executive Metrics Row
                col1, col2, col3, col4 = st.columns(4)
                col1.metric(
                    label="Quoted Monthly Premium",
                    value=f"${pricing['final_monthly_premium']:,.2f}",
                )
                col2.metric(
                    label="Quoted Annual Premium",
                    value=f"${pricing['final_annual_premium']:,.2f}",
                )
                col3.metric(
                    label=f"CMS {loc['state_code']} Benchmark Rate",
                    value=f"${cms_benchmark:,.2f}/mo",
                    help="State-level average for standard Silver Benchmark Qualified Health Plan",
                )
                variance = round(
                    ((pricing["final_monthly_premium"] - cms_benchmark) / cms_benchmark) * 100,
                    1,
                )
                col4.metric(
                    label="Benchmark Variance",
                    value=f"{'+' if variance > 0 else ''}{variance}%",
                    delta=f"{variance}% vs base",
                    delta_color="inverse",
                )

                st.divider()

                # 3. Two-Column Layout: Cost Breakdown & Counterfactual Savings
                col_left, col_right = st.columns([1, 1])

                with col_left:
                    st.subheader("📊 Itemized Actuarial Waterfall")
                    st.write("Deterministic breakdown based on Title 45 CFR § 147.102 rating rules:")

                    breakdown_data = {
                        "Base Annual Benchmark": f"${cms_benchmark * 12:,.2f}",
                        "Statutory Age Curve Factor": f"{breakdown['age_factor']}x",
                        "Age-Adjusted Annual Base": f"${breakdown['base_annual_premium']:,.2f}",
                        "Tobacco Surcharge (45%)": f"+${breakdown['tobacco_surcharge']:,.2f}",
                        "Metabolic BMI Surcharge": f"+${breakdown['bmi_surcharge']:,.2f}",
                        "Hypertension Surcharge": f"+${breakdown['hypertension_surcharge']:,.2f}",
                        f"Dependents Allowance ({breakdown['chargeable_children']} chargeable)": f"+${breakdown['dependents_surcharge']:,.2f}",
                        "Total Calculated Premium": f"${pricing['final_annual_premium']:,.2f}",
                    }
                    st.table(breakdown_data)

                with col_right:
                    st.subheader("💡 Counterfactual Savings Scenarios")
                    st.write("Automated mitigation pathways computed for applicant risk factors:")

                    if counterfactuals:
                        for key, scenario in counterfactuals.items():
                            st.markdown(
                                f"""
                                <div class="savings-card">
                                    <h4 style="margin: 0; color: #2e7d32;">🎯 {key.replace('_', ' ').title()}</h4>
                                    <p style="margin: 5px 0;"><strong>Action:</strong> {scenario['action']}</p>
                                    <p style="margin: 0;"><strong>Annual Savings:</strong> <span style="color: #2e7d32; font-weight: bold;">-${scenario['annual_savings_usd']:,.2f}</span> (-${scenario['monthly_savings_usd']:,.2f}/mo)</p>
                                    <p style="margin: 0;"><strong>Revised Annual Premium:</strong> ${scenario['revised_annual_premium']:,.2f}</p>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                    else:
                        st.info("No discretionary surcharges detected. Applicant qualifies for standard baseline rates.")

                st.divider()

                # 4. Underwriting AI Synthesis
                st.subheader("📑 Regulatory Audit & Grounded Synthesis (GPT-6 Luna)")
                st.markdown(synthesis)

            else:
                st.error(f"Backend API returned status code {res.status_code} from `{target_url}`: {res.text}")

        except httpx.ConnectError as e:
            st.error(
                f"❌ Connection error reaching `{target_url}`: {str(e)}\n\n"
                "If running in Docker, ensure the backend container (`actuarial_api`) is running on `http://api:8000`."
            )
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")
else:
    st.info("👈 Enter the applicant's details in the sidebar and click **'Evaluate Application & Calculate Quote'** to run the agent.")