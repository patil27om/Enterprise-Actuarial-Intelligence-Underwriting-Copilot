"""Verification Test for LangGraph Underwriting Workflow."""

import asyncio
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.graph.workflow import underwriting_graph


async def run_test():
    # Ensure OPENAI_API_KEY is present
    if not os.getenv("OPENAI_API_KEY"):
        print(
            "[!] Error: OPENAI_API_KEY is not set. Please set it in your .env file."
        )
        return

    sample_applicant = {
        "age": 45,
        "gender": "male",
        "bmi": 29.5,
        "smoker": "Yes",
        "children": 2,
        "bloodpressure": 125,
        "zipcode": "33101",
    }

    initial_state = {
        "applicant_data": sample_applicant,
        "geo_data": {},
        "benchmark_rate_monthly": 0.0,
        "pricing_data": {},
        "retrieved_clauses": [],
        "counterfactual_scenarios": {},
        "final_synthesis": "",
    }

    print("[*] Initiating LangGraph Execution...")
    final_state = await underwriting_graph.ainvoke(initial_state)

    print("\n[+] --- EXECUTION SUMMARY ---")
    print(
        f"Location: {final_state['geo_data']['city']}, {final_state['geo_data']['state']} (ZIP {final_state['geo_data']['zipcode']})"
    )
    print(
        f"Calculated Premium: ${final_state['pricing_data']['final_monthly_premium']}/mo (${final_state['pricing_data']['final_annual_premium']}/yr)"
    )
    print(f"Retrieved Policy Clauses: {len(final_state['retrieved_clauses'])}")
    print(
        f"Counterfactual Scenarios Generated: {list(final_state['counterfactual_scenarios'].keys())}"
    )

    print("\n[+] --- GPT-6 LUNA ACTUARIAL SYNTHESIS ---")
    print(final_state["final_synthesis"])
    print("\n[SUCCESS] LangGraph workflow executed successfully.")


if __name__ == "__main__":
    asyncio.run(run_test())