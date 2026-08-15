"""
alliance_partner_mcp.py - MCP Server 2: Alliance Partner Inventory & Rebooking Engine

Exposes MCP tools to search Star Alliance / Oneworld / SkyTeam partner flights
and evaluate optimal interline rerouting options for disrupted passengers.

Communicates with MCP clients over stdio transport.
"""

import sys
import warnings

warnings.filterwarnings("ignore", message=".*lifespan.*")

from mcp.server.fastmcp import FastMCP
import airline_db

mcp = FastMCP("Alliance Partner Service", log_level="WARNING")


@mcp.tool()
def search_alliance_alternatives(origin: str, destination: str, cabin_class: str = "Business"):
    """Search for available seats across Star Alliance, Oneworld, and SkyTeam partner airlines for a route (e.g. DEL -> LHR, BOM -> FRA, BLR -> NRT)."""
    options = airline_db.find_alliance_flights(origin, destination, cabin_class)
    if not options:
        return f"No alliance partner seats available for route {origin} -> {destination} in {cabin_class} class."

    lines = [f"=== ALLIANCE PARTNER FLIGHT INVENTORY ({origin} -> {destination}) ==="]
    for idx, opt in enumerate(options, 1):
        lines.append(
            f"Option {idx}: [{opt['alliance']}] {opt['airline']} - Flight {opt['flight_number']}\n"
            f"  Departure: {opt['departure_time']} | Arrival: {opt['arrival_time']}\n"
            f"  Cabin    : {opt['cabin_class']} | Available Seats: {opt['seats_available']}\n"
            f"  Interline Agreement Code: {opt['interline_code']}\n"
        )
    return "\n".join(lines)


@mcp.tool()
def evaluate_rebooking_options(pnr_code: str = "AI9482"):
    """Analyze and rank the best alternative itineraries for a disrupted PNR based on layover time, alliance compatibility, and seat availability."""
    pnr = airline_db.get_pnr(pnr_code)
    if not pnr:
        return f"PNR '{pnr_code}' not found."

    options = airline_db.find_alliance_flights(pnr['origin'], pnr['destination'], pnr['cabin_class'])
    if not options:
        return f"No rebooking options found for PNR {pnr_code} ({pnr['origin']} -> {pnr['destination']})."

    output = [
        f"=== REBOOKING EVALUATION REPORT FOR PNR: {pnr['pnr_code']} ({pnr['passenger_name']}) ===",
        f"Original Flight: {pnr['airline']} {pnr['flight_number']} ({pnr['origin']} -> {pnr['destination']}) - CANCELLED",
        f"Cabin Class    : {pnr['cabin_class']}\n",
        "RECOMMENDED REBOOKING ITINERARIES (Ranked by IATA Protection Priority):",
    ]

    for idx, opt in enumerate(options, 1):
        score = "HIGH (Direct Alliance Partner)" if "Star Alliance" in opt['alliance'] else "MEDIUM (Interline Partner)"
        output.append(
            f"#{idx}. {opt['airline']} ({opt['flight_number']})\n"
            f"    Alliance Group : {opt['alliance']}\n"
            f"    Schedule       : Departs {opt['departure_time']}, Arrives {opt['arrival_time']}\n"
            f"    Protection Rank: {score}\n"
            f"    Interline Code : {opt['interline_code']}"
        )

    output.append("\nRecommendation: Issue e-ticket on Option #1 to minimize passenger delay.")
    return "\n".join(output)


if __name__ == "__main__":
    if sys.stdin.isatty():
        print("This is an MCP server - a client starts it. Run airline_capstone.py to test.", file=sys.stderr)
        raise SystemExit(0)
    mcp.run(transport="stdio")
