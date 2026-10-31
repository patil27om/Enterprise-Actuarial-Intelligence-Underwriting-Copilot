"""API Route Handlers."""

import logging
from app.api.schemas import QuoteRequest, QuoteResponse
from app.graph.workflow import underwriting_graph
from fastapi import APIRouter, HTTPException, status

logger = logging.getLogger("uvicorn.error")

router = APIRouter(prefix="/api/v1", tags=["Underwriting"])


@router.post(
    "/quote",
    response_model=QuoteResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Actuarial Quote & Underwriting Audit",
)
async def generate_quote(request: QuoteRequest):
    """Executes the LangGraph underwriting state machine:

    1. Resolves geolocation via public postal geocoder.
    2. Ingests live state CMS Silver Plan benchmarks.
    3. Calculates ACA statutory age adjustments and surcharges.
    4. Dynamically routes to counterfactual savings analysis.
    5. Retrieves grounding policy clauses from ChromaDB.
    6. Generates a synthesis using gpt-6-luna.
    """
    try:
        initial_state = {
            "applicant_data": request.model_dump(),
            "geo_data": {},
            "benchmark_rate_monthly": 0.0,
            "pricing_data": {},
            "retrieved_clauses": [],
            "counterfactual_scenarios": {},
            "final_synthesis": "",
        }

        # Asynchronously run LangGraph state machine
        final_state = await underwriting_graph.ainvoke(initial_state)

        return QuoteResponse(
            location=final_state["geo_data"],
            benchmark_rate_monthly=final_state["benchmark_rate_monthly"],
            pricing=final_state["pricing_data"],
            retrieved_clauses_count=len(final_state.get("retrieved_clauses", [])),
            counterfactual_scenarios=final_state.get("counterfactual_scenarios", {}),
            underwriting_synthesis=final_state["final_synthesis"],
        )

    except Exception as exc:
        logger.error(f"Underwriting execution failed: {str(exc)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Actuarial evaluation error: {str(exc)}",
        )