import asyncio
import sys
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.mcp_servers import resolve_zipcode, get_state_benchmark, calculate_actuarial_quote


async def main():
    print("[*] Testing Tool 1: Live Geo Resolver (ZIP 33101 - Miami, FL)...")
    geo = await resolve_zipcode("33101")
    print(f"    Resolved: {geo['city']}, {geo['state']} ({geo['state_code']}) | Region: {geo['region']}")

    print("\n[*] Testing Tool 2: CMS Benchmark Provider...")
    cms = get_state_benchmark(geo["state_code"])
    print(f"    State Benchmark: ${cms['monthly_benchmark_usd']}/month (${cms['annual_benchmark_usd']}/year)")

    print("\n[*] Testing Tool 3: Actuarial Pricing Engine (Age 45, Smoker=Yes, BMI 29.5, Children 2)...")
    quote = calculate_actuarial_quote(
        age=45.0,
        bmi=29.5,
        smoker="Yes",
        children=2,
        monthly_benchmark=cms["monthly_benchmark_usd"],
        bloodpressure=125,
    )
    print(f"    Monthly Premium: ${quote['final_monthly_premium']}")
    print(f"    Annual Premium:  ${quote['final_annual_premium']}")
    print("    Breakdown:")
    for k, v in quote["breakdown"].items():
        print(f"      - {k}: {v}")

    print("\n[SUCCESS] All MCP tools verified successfully.")


if __name__ == "__main__":
    asyncio.run(main())