"""
passenger_welfare_mcp.py - MCP Server 3: Passenger Welfare & Interline E-Ticketing

Exposes MCP tools to re-issue interline e-tickets across alliance airlines,
update automated IATA baggage transfers, and issue hotel/lounge vouchers.

Communicates with MCP clients over stdio transport.
"""

import sys
import random
import warnings

warnings.filterwarnings("ignore", message=".*lifespan.*")

from mcp.server.fastmcp import FastMCP
import airline_db

mcp = FastMCP("Passenger Welfare & Interline Service", log_level="WARNING")


@mcp.tool()
def issue_interline_ticket(pnr_code: str = "AI9482", partner_airline: str = "Lufthansa", new_flight_numbers: str = "LH-761 / LH-900"):
    """Re-issue passenger electronic ticket (e-Ticket) on an alliance partner airline under IATA Resolution 735d without charging the passenger."""
    pnr = airline_db.get_pnr(pnr_code)
    if not pnr:
        return f"PNR '{pnr_code}' not found."

    ticket_no = f"083-{random.randint(1000000000, 9999999999)}"
    bag_tag = f"BAG-INT-{random.randint(10000, 99999)}"
    voucher = f"VOUCH-LUX-{random.randint(100, 999)}"

    # Save transaction in database
    airline_db.record_rebooking(
        pnr_code=pnr_code,
        new_flight_numbers=new_flight_numbers,
        partner_airline=partner_airline,
        ticket_no=ticket_no,
        bag_tag=bag_tag,
        voucher=voucher,
    )

    return (
        f"=== INTERLINE E-TICKET RE-ISSUED SUCCESSFULLY ===\n"
        f"PNR Code        : {pnr['pnr_code']}\n"
        f"Passenger Name  : {pnr['passenger_name']}\n"
        f"Original Airline: {pnr['airline']} (Flight Cancelled)\n"
        f"New Carrier     : {partner_airline}\n"
        f"New Flight(s)   : {new_flight_numbers}\n"
        f"Cabin Class     : {pnr['cabin_class']} (Protected)\n"
        f"IATA e-Ticket No: {ticket_no}\n"
        f"Total Fee Charged: $0.00 (Covered under Alliance Protection Agreement)"
    )


@mcp.tool()
def transfer_baggage_tags(pnr_code: str = "AI9482", new_flight_numbers: str = "LH-761 / LH-900"):
    """Update automated IATA baggage routing tags so checked bags are automatically transferred to the new partner flights."""
    pnr = airline_db.get_pnr(pnr_code)
    if not pnr:
        return f"PNR '{pnr_code}' not found."

    tag_id = f"IATA-TAG-{pnr_code}-{random.randint(1000, 9999)}"
    return (
        f"=== BAGGAGE RE-ROUTING COMPLETED ===\n"
        f"PNR Code      : {pnr['pnr_code']}\n"
        f"Passenger     : {pnr['passenger_name']}\n"
        f"Checked Bags  : {pnr['baggage_count']} Bag(s)\n"
        f"New Routing   : Transferred to {new_flight_numbers}\n"
        f"Interline Tag : {tag_id}\n"
        f"Status        : Baggage tracking system updated. Bags will automatically transfer at hub airport."
    )


@mcp.tool()
def issue_welfare_vouchers(pnr_code: str = "AI9482", layover_hours: float = 4.5):
    """Generate airport lounge access, meal coupons, and hotel vouchers based on connection layover duration."""
    pnr = airline_db.get_pnr(pnr_code)
    if not pnr:
        return f"PNR '{pnr_code}' not found."

    lounge_pass = f"STAR-LOUNGE-{random.randint(10000, 99999)}"
    meal_voucher = f"MEAL-USD50-{random.randint(1000, 9999)}"
    
    hotel_info = ""
    if layover_hours >= 6.0:
        hotel_info = f"\n  - Transit Hotel Stay Voucher: Airport Transit Hotel (Room Pass: H-{random.randint(100, 999)})"

    return (
        f"=== PASSENGER WELFARE VOUCHERS ISSUED ===\n"
        f"PNR Code     : {pnr['pnr_code']}\n"
        f"Passenger    : {pnr['passenger_name']} ({pnr['cabin_class']} Class)\n"
        f"Layover Time : {layover_hours} Hours\n"
        f"Vouchers Generated:\n"
        f"  - Star Alliance Business Lounge Pass: {lounge_pass}\n"
        f"  - Airport Dining Voucher           : {meal_voucher} ($50 USD value){hotel_info}\n"
        f"Notification : Sent via SMS and email to passenger."
    )


if __name__ == "__main__":
    if sys.stdin.isatty():
        print("This is an MCP server - a client starts it. Run airline_capstone.py to test.", file=sys.stderr)
        raise SystemExit(0)
    mcp.run(transport="stdio")
