"""
airline_disruption_mcp.py - MCP Server 1: PNR & Flight Disruption Service

Exposes MCP tools for looking up passenger PNRs, flight cancellation reasons,
and disruption status reports.

Communicates with MCP clients over stdio transport.
"""

import sys
import warnings

warnings.filterwarnings("ignore", message=".*lifespan.*")

from mcp.server.fastmcp import FastMCP
import airline_db

mcp = FastMCP("Airline Disruption Service", log_level="WARNING")


@mcp.tool()
def get_pnr_details(pnr_code: str = "AI9482"):
    """Look up passenger booking, flight details, cancellation status, and baggage count by PNR code (e.g. AI9482, LH4081, SQ2319)."""
    pnr = airline_db.get_pnr(pnr_code)
    if not pnr:
        return f"PNR Record '{pnr_code}' not found in global reservation system."

    status_str = f"Flight {pnr['flight_number']} ({pnr['origin']} -> {pnr['destination']}) is CANCELLED." if pnr['status'] == "CANCELLED" else f"Status: {pnr['status']}"

    return (
        f"=== PNR RECORD: {pnr['pnr_code']} ===\n"
        f"Passenger Name : {pnr['passenger_name']}\n"
        f"Original Flight: {pnr['airline']} ({pnr['flight_number']})\n"
        f"Route          : {pnr['origin']} -> {pnr['destination']} on {pnr['flight_date']}\n"
        f"Cabin Class    : {pnr['cabin_class']}\n"
        f"Baggage Count  : {pnr['baggage_count']} Checked Bag(s)\n"
        f"Current Status : {status_str}\n"
        f"Disruption Cause: {pnr['disruption_reason']}"
    )


@mcp.tool()
def get_disruption_report(flight_number: str = "AI-101"):
    """Fetch the official operational disruption log and cancellation reason for a specific flight."""
    conn = airline_db.sqlite3.connect(airline_db.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT flight_number, airline, origin, destination, status, disruption_reason FROM pnrs WHERE flight_number = ?", (flight_number.upper().strip(),))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return f"No disruption log filed for flight {flight_number}."

    return (
        f"=== OFFICIAL DISRUPTION LOG ===\n"
        f"Flight      : {row[1]} {row[0]} ({row[2]} -> {row[3]})\n"
        f"Status      : {row[4]}\n"
        f"Details     : {row[5]}\n"
        f"IATA Policy : Interline protection mandated. Partner carrier re-accommodation authorized."
    )


if __name__ == "__main__":
    if sys.stdin.isatty():
        print("This is an MCP server - a client starts it. Run airline_capstone.py to test.", file=sys.stderr)
        raise SystemExit(0)
    mcp.run(transport="stdio")
