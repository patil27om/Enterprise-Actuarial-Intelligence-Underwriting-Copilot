"""Geo Resolver MCP Tool.

Resolves US postal codes to municipal locations and ACA geographic rating regions.
"""

import httpx

# Mapping US state abbreviations to regional rating territories
STATE_REGION_MAP = {
    # Northeast
    "ME": "northeast", "NH": "northeast", "VT": "northeast", "MA": "northeast",
    "RI": "northeast", "CT": "northeast", "NY": "northeast", "PA": "northeast", "NJ": "northeast",
    # Southeast
    "FL": "southeast", "GA": "southeast", "NC": "southeast", "SC": "southeast",
    "VA": "southeast", "WV": "southeast", "KY": "southeast", "TN": "southeast",
    "AL": "southeast", "MS": "southeast", "LA": "southeast", "AR": "southeast",
    # Midwest
    "OH": "midwest", "IN": "midwest", "IL": "midwest", "MI": "midwest",
    "WI": "midwest", "MN": "midwest", "IA": "midwest", "MO": "midwest",
    "ND": "midwest", "SD": "midwest", "NE": "midwest", "KS": "midwest",
    # Southwest
    "TX": "southwest", "AZ": "southwest", "NM": "southwest", "OK": "southwest",
    # Northwest / West
    "WA": "northwest", "OR": "northwest", "ID": "northwest", "MT": "northwest",
    "WY": "northwest", "CO": "west", "UT": "west", "NV": "west",
    "CA": "west", "AK": "northwest", "HI": "west",
}


async def resolve_zipcode(zipcode: str) -> dict:
    """Resolves a 5-digit US ZIP code to city, state, state abbreviation, and geographic rating region."""
    cleaned_zip = str(zipcode).strip()[:5]
    url = f"https://api.zippopotam.us/us/{cleaned_zip}"

    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                place = data["places"][0]
                state_abbr = place["state abbreviation"]
                return {
                    "zipcode": cleaned_zip,
                    "city": place["place name"],
                    "state": place["state"],
                    "state_code": state_abbr,
                    "region": STATE_REGION_MAP.get(state_abbr, "southeast"),
                    "status": "resolved",
                }
        except Exception:
            pass

    # Graceful fallback if offline or invalid ZIP
    return {
        "zipcode": cleaned_zip,
        "city": "Metro Area",
        "state": "Florida",
        "state_code": "FL",
        "region": "southeast",
        "status": "fallback",
    }