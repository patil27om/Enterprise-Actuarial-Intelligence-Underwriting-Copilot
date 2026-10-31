"""Tests for FastAPI endpoints and Pydantic validation."""

import pytest
import httpx
from app.main import app


@pytest.mark.asyncio
async def test_health_check_endpoint():
    """Verifies that /health endpoint is live."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://test"
    ) as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {
            "status": "healthy",
            "service": "insurance-actuarial-agent",
        }


@pytest.mark.asyncio
async def test_quote_endpoint_validation_error():
    """Verifies that invalid payloads trigger a 422 Unprocessable Entity."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://test"
    ) as client:
        invalid_payload = {
            "age": 12,
            "gender": "male",
            "bmi": 24.0,
            "smoker": "No",
            "zipcode": "123",
        }
        response = await client.post("/api/v1/quote", json=invalid_payload)
        assert response.status_code == 422