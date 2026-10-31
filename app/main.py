"""FastAPI Application Entry Point."""

from app.api.routes import router as api_router
from app.config import API_HOST, API_PORT
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="Enterprise Actuarial & Underwriting AI Engine",
    description="Live API Data Enrichment | LangGraph State Machine | GPT-6 Luna RAG Explainer",
    version="1.0.0",
)

# Enable CORS for web frontends (e.g., Streamlit, React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(api_router)


@app.get("/health", tags=["System"])
async def health_check():
    """Liveness check for deployment monitoring."""
    return {"status": "healthy", "service": "insurance-actuarial-agent"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host=API_HOST, port=API_PORT, reload=True)