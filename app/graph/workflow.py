"""Workflow Definition & Graph Compilation."""

from app.graph.nodes import (
    node_calculate_pricing,
    node_compute_counterfactuals,
    node_enrich_market,
    node_retrieve_policies,
    node_synthesize_recommendation,
)
from app.graph.state import UnderwritingState
from langgraph.graph import END, START, StateGraph


def condition_check_surcharges(state: UnderwritingState) -> str:
    """Conditional Edge: Routes high-risk profiles to counterfactual calculations."""
    breakdown = state["pricing_data"]["breakdown"]
    has_tobacco = breakdown["tobacco_surcharge"] > 0
    has_bmi = breakdown["bmi_surcharge"] > 0
    has_hypertension = breakdown["hypertension_surcharge"] > 0

    if has_tobacco or has_bmi or has_hypertension:
        return "node_compute_counterfactuals"
    return "node_retrieve_policies"


def build_underwriting_graph():
    """Builds and compiles the LangGraph workflow."""
    builder = StateGraph(UnderwritingState)

    # Add Nodes
    builder.add_node("node_enrich_market", node_enrich_market)
    builder.add_node("node_calculate_pricing", node_calculate_pricing)
    builder.add_node(
        "node_compute_counterfactuals", node_compute_counterfactuals
    )
    builder.add_node("node_retrieve_policies", node_retrieve_policies)
    builder.add_node(
        "node_synthesize_recommendation", node_synthesize_recommendation
    )

    # Edge Transitions
    builder.add_edge(START, "node_enrich_market")
    builder.add_edge("node_enrich_market", "node_calculate_pricing")

    # Conditional Branching based on Risk Surcharges
    builder.add_conditional_edges(
        "node_calculate_pricing",
        condition_check_surcharges,
        {
            "node_compute_counterfactuals": "node_compute_counterfactuals",
            "node_retrieve_policies": "node_retrieve_policies",
        },
    )

    builder.add_edge("node_compute_counterfactuals", "node_retrieve_policies")
    builder.add_edge(
        "node_retrieve_policies", "node_synthesize_recommendation"
    )
    builder.add_edge("node_synthesize_recommendation", END)

    return builder.compile()


# Singleton compiled graph instance
underwriting_graph = build_underwriting_graph()