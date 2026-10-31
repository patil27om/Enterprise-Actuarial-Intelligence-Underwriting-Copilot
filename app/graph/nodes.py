"""LangGraph Processing Nodes."""

from typing import Any, Dict
from app.core.llm import get_llm
from app.core.vectorstore import get_vectorstore
from app.graph.state import UnderwritingState
from app.mcp_servers import (
    calculate_actuarial_quote,
    get_state_benchmark,
    resolve_zipcode,
)
from langchain_core.messages import SystemMessage, HumanMessage


async def node_enrich_market(state: UnderwritingState) -> Dict[str, Any]:
    """Resolves ZIP code via public geocoder and pulls state CMS benchmark."""
    zipcode = state["applicant_data"].get("zipcode", "33101")
    geo = await resolve_zipcode(zipcode)
    cms = get_state_benchmark(geo["state_code"])

    return {
        "geo_data": geo,
        "benchmark_rate_monthly": cms["monthly_benchmark_usd"],
    }


def node_calculate_pricing(state: UnderwritingState) -> Dict[str, Any]:
    """Calculates actuarial pricing using deterministic ACA formulas."""
    app_data = state["applicant_data"]
    benchmark = state["benchmark_rate_monthly"]

    pricing = calculate_actuarial_quote(
        age=float(app_data["age"]),
        bmi=float(app_data["bmi"]),
        smoker=str(app_data["smoker"]),
        children=int(app_data.get("children", 0)),
        monthly_benchmark=benchmark,
        bloodpressure=int(app_data.get("bloodpressure", 120)),
    )
    return {"pricing_data": pricing}


def node_retrieve_policies(state: UnderwritingState) -> Dict[str, Any]:
    """Queries local ChromaDB for policy rules matching the applicant's risk factors."""
    app_data = state["applicant_data"]
    vectorstore = get_vectorstore()

    # Formulate a targeted retrieval query
    query_parts = ["underwriting rules"]
    if str(app_data.get("smoker")).lower() in ["yes", "true", "1"]:
        query_parts.append("tobacco surcharge cessation exemption")
    if float(app_data.get("bmi", 22.0)) > 25.0:
        query_parts.append("metabolic BMI tiers obesity loading")
    if int(app_data.get("children", 0)) > 0:
        query_parts.append("family dependent child allowances")

    query = " ".join(query_parts)
    docs = vectorstore.similarity_search(query, k=3)
    clauses = [doc.page_content for doc in docs]

    return {"retrieved_clauses": clauses}


def node_compute_counterfactuals(state: UnderwritingState) -> Dict[str, Any]:
    """Calculates mathematical what-if reduction scenarios for high-risk surcharges."""
    pricing = state["pricing_data"]
    breakdown = pricing["breakdown"]
    scenarios: Dict[str, Any] = {}

    # Tobacco Cessation Scenario
    if breakdown["tobacco_surcharge"] > 0:
        savings_annual = breakdown["tobacco_surcharge"]
        scenarios["tobacco_cessation"] = {
            "action": "Enroll in an approved 90-day Tobacco Cessation Program (Title 45 CFR § 147.102)",
            "annual_savings_usd": savings_annual,
            "monthly_savings_usd": round(savings_annual / 12.0, 2),
            "revised_annual_premium": round(
                pricing["final_annual_premium"] - savings_annual, 2
            ),
        }

    # BMI Metabolic Normalization Scenario
    if breakdown["bmi_surcharge"] > 0:
        savings_annual = breakdown["bmi_surcharge"]
        scenarios["bmi_normalization"] = {
            "action": "Maintain documented participation in certified wellness program reaching BMI < 25.0",
            "annual_savings_usd": savings_annual,
            "monthly_savings_usd": round(savings_annual / 12.0, 2),
            "revised_annual_premium": round(
                pricing["final_annual_premium"] - savings_annual, 2
            ),
        }

    return {"counterfactual_scenarios": scenarios}


def node_synthesize_recommendation(state: UnderwritingState) -> Dict[str, Any]:
    """Generates an audit-ready, grounded actuarial explanation using gpt-6-luna."""
    llm = get_llm()
    app_data = state["applicant_data"]
    geo = state["geo_data"]
    pricing = state["pricing_data"]
    clauses = "\n\n---\n\n".join(state.get("retrieved_clauses", []))
    scenarios = state.get("counterfactual_scenarios", {})

    system_instruction = (
        "You are an expert AI Health Insurance Actuary & Underwriting Advisor. "
        "Your task is to generate a professional, audit-compliant quote breakdown "
        "strictly grounded in the provided calculation data and regulatory clauses."
    )

    user_prompt = f"""
APPLICANT PROFILE:
- Age: {app_data['age']} | Gender: {app_data.get('gender', 'N/A')} | BMI: {app_data['bmi']}
- Tobacco User: {app_data['smoker']} | Dependents: {app_data.get('children', 0)} | Blood Pressure: {app_data.get('bloodpressure', 120)}
- Location: {geo['city']}, {geo['state']} (Rating Area: {geo['region'].upper()}, ZIP: {geo['zipcode']})

ACTUARIAL COMPUTATION BREAKDOWN:
- Monthly Quote: ${pricing['final_monthly_premium']} | Annual Quote: ${pricing['final_annual_premium']}
- State Benchmark (Silver Plan Base): ${state['benchmark_rate_monthly']}/month
- Statutory Age Factor (3:1 curve): {pricing['breakdown']['age_factor']}x
- Base Age-Adjusted Annual: ${pricing['breakdown']['base_annual_premium']}
- Tobacco Surcharge: +${pricing['breakdown']['tobacco_surcharge']}
- Excess BMI Surcharge: +${pricing['breakdown']['bmi_surcharge']}
- Dependents Cost: +${pricing['breakdown']['dependents_surcharge']} ({pricing['breakdown']['chargeable_children']} chargeable)

REGULATORY CLAUSES RETRIEVED:
{clauses}

COUNTERFACTUAL SAVINGS SCENARIOS COMPUTED:
{scenarios}

DELIVERABLE FORMAT:
1. Executive Underwriting Summary: Explain why the premium was set to this specific figure based on the applicant's profile.
2. Regulatory Compliance: Cite Title 45 CFR § 147.102 and CMS 3:1 age-curve rules governing these specific charges.
3. Actionable Path to Rate Reduction: Detail the counterfactual savings options (with exact dollar figures) to show how the applicant can lower their premium.
"""

    messages = [
        SystemMessage(content=system_instruction),
        HumanMessage(content=user_prompt),
    ]

    response = llm.invoke(messages)
    return {"final_synthesis": response.content}