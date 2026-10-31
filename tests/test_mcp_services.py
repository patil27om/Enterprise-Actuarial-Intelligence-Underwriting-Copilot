"""Integration tests for MCP geocoding and CMS benchmark tools."""

import pytest
from app.mcp_servers.geo_mcp import resolve_zipcode
from app.mcp_servers.cms_benchmarks_mcp import get_state_benchmark


@pytest.mark.asyncio
async def test_resolve_valid_zipcode():
    """Tests live Zippopotam geocoder resolution for Miami, FL (33101)."""
    res = await resolve_zipcode("33101")
    assert res["status"] == "resolved"
    assert res["state_code"] == "FL"
    assert res["region"] == "southeast"
    assert "Miami" in res["city"]


@pytest.mark.asyncio
async def test_resolve_invalid_zipcode_fallback():
    """Tests fallback resilience when given an unresolvable ZIP code."""
    res = await resolve_zipcode("00000")
    assert res["status"] in ["resolved", "fallback"]
    assert "state_code" in res
    assert "region" in res


def test_cms_benchmark_lookup():
    """Tests state baseline rate lookup against CMS reference indices."""
    fl_bench = get_state_benchmark("FL")
    assert fl_bench["monthly_benchmark_usd"] == 480.0
    assert fl_bench["annual_benchmark_usd"] == 5760.0

    ny_bench = get_state_benchmark("NY")
    assert ny_bench["monthly_benchmark_usd"] == 690.0

    unknown_bench = get_state_benchmark("ZZ")
    assert unknown_bench["monthly_benchmark_usd"] == 490.0