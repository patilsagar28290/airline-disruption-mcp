"""
airline_db.py - SQLite Database for Airline Disruption & Alliance Interline Rebooking

Manages the local database (airline.db) containing passenger PNR records,
cancelled flights, alliance partner flight inventory (Star Alliance, SkyTeam, Oneworld),
and rebooking history logs.
"""

import os
import sqlite3
import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "airline.db")


def _setup():
    """Create tables and seed realistic sample data for airline disruption scenarios."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. PNRs Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pnrs (
            pnr_code TEXT PRIMARY KEY,
            passenger_name TEXT,
            flight_number TEXT,
            airline TEXT,
            origin TEXT,
            destination TEXT,
            flight_date TEXT,
            cabin_class TEXT,
            baggage_count INTEGER,
            status TEXT,
            disruption_reason TEXT
        )
    """)

    # 2. Alliance Flight Inventory Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alliance_inventory (
            inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
            airline TEXT,
            flight_number TEXT,
            alliance TEXT,
            origin TEXT,
            destination TEXT,
            flight_date TEXT,
            departure_time TEXT,
            arrival_time TEXT,
            cabin_class TEXT,
            seats_available INTEGER,
            interline_code TEXT
        )
    """)

    # 3. Rebookings Log Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rebookings (
            rebooking_id INTEGER PRIMARY KEY AUTOINCREMENT,
            pnr_code TEXT,
            new_flight_numbers TEXT,
            partner_airline TEXT,
            interline_ticket_no TEXT,
            baggage_tag_id TEXT,
            voucher_details TEXT,
            created_at TEXT
        )
    """)

    # Seed Sample PNRs
    sample_pnrs = [
        (
            "AI9482",
            "Aarav Sharma",
            "AI-101",
            "Air India",
            "DEL",
            "LHR",
            "2026-08-16",
            "Business",
            2,
            "CANCELLED",
            "Technical Snag: Hydraulic Pump Pressure Failure on AI-101 aircraft.",
        ),
        (
            "LH4081",
            "Priya Patel",
            "LH-757",
            "Lufthansa",
            "BOM",
            "FRA",
            "2026-08-16",
            "Economy",
            1,
            "CANCELLED",
            "Operational Disruption: Frankfurt Airport Ground Staff Strike.",
        ),
        (
            "SQ2319",
            "Rahul Verma",
            "SQ-503",
            "Singapore Airlines",
            "BLR",
            "NRT",
            "2026-08-16",
            "Business",
            2,
            "CANCELLED",
            "Severe Weather: Super Typhoon approaching Changi Transit Hub.",
        ),
    ]

    cursor.executemany(
        "INSERT OR IGNORE INTO pnrs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        sample_pnrs,
    )

    # Clear existing inventory and re-seed fresh options for demo consistency
    cursor.execute("DELETE FROM alliance_inventory")

    sample_inventory = [
        # DEL -> LHR Alternatives (Star Alliance / Partner airlines)
        ("Lufthansa", "LH-761 / LH-900", "Star Alliance", "DEL", "LHR", "2026-08-16", "03:30 IST", "14:15 BST", "Business", 4, "STAR-INT-9921"),
        ("Swiss Air", "LX-147 / LX-316", "Star Alliance", "DEL", "LHR", "2026-08-16", "01:15 IST", "13:45 BST", "Business", 2, "STAR-INT-8834"),
        ("British Airways", "BA-142", "Oneworld", "DEL", "LHR", "2026-08-16", "10:20 IST", "15:05 BST", "Business", 1, "OW-INT-4410"),
        ("Emirates", "EK-511 / EK-029", "Interline Partner", "DEL", "LHR", "2026-08-16", "04:15 IST", "16:20 BST", "Business", 3, "EK-INT-7712"),

        # BOM -> FRA Alternatives
        ("Swiss Air", "LX-155 / LX-363", "Star Alliance", "BOM", "FRA", "2026-08-16", "01:20 IST", "11:50 CEST", "Economy", 8, "STAR-INT-5519"),
        ("Qatar Airways", "QR-557 / QR-069", "Oneworld", "BOM", "FRA", "2026-08-16", "04:10 IST", "13:30 CEST", "Economy", 6, "OW-INT-3381"),
        ("Air India", "AI-131", "Star Alliance", "BOM", "LHR", "2026-08-16", "06:45 IST", "11:30 BST", "Economy", 5, "STAR-INT-9011"),

        # BLR -> NRT Alternatives
        ("Thai Airways", "TG-326 / TG-676", "Star Alliance", "BLR", "NRT", "2026-08-16", "01:05 IST", "15:50 JST", "Business", 3, "STAR-INT-1192"),
        ("ANA (All Nippon Airways)", "NH-814", "Star Alliance", "BLR", "NRT", "2026-08-16", "20:00 IST", "07:30 JST (+1)", "Business", 2, "STAR-INT-2245"),
        ("Cathay Pacific", "CX-646 / CX-500", "Oneworld", "BLR", "NRT", "2026-08-16", "02:30 IST", "16:15 JST", "Business", 4, "OW-INT-6618"),
    ]

    cursor.executemany(
        "INSERT INTO alliance_inventory (airline, flight_number, alliance, origin, destination, flight_date, departure_time, arrival_time, cabin_class, seats_available, interline_code) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        sample_inventory,
    )

    conn.commit()
    conn.close()


def get_pnr(pnr_code: str):
    """Fetch PNR record from database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pnrs WHERE pnr_code = ?", (pnr_code.upper().strip(),))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "pnr_code": row[0],
        "passenger_name": row[1],
        "flight_number": row[2],
        "airline": row[3],
        "origin": row[4],
        "destination": row[5],
        "flight_date": row[6],
        "cabin_class": row[7],
        "baggage_count": row[8],
        "status": row[9],
        "disruption_reason": row[10],
    }


def find_alliance_flights(origin: str, destination: str, cabin_class: str = "Business"):
    """Query alliance flight inventory matching route and cabin class."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """SELECT airline, flight_number, alliance, origin, destination, departure_time, arrival_time, cabin_class, seats_available, interline_code 
           FROM alliance_inventory 
           WHERE origin = ? AND destination = ? AND seats_available > 0""",
        (origin.upper().strip(), destination.upper().strip()),
    )
    rows = cursor.fetchall()
    conn.close()
    results = []
    for r in rows:
        results.append({
            "airline": r[0],
            "flight_number": r[1],
            "alliance": r[2],
            "origin": r[3],
            "destination": r[4],
            "departure_time": r[5],
            "arrival_time": r[6],
            "cabin_class": r[7],
            "seats_available": r[8],
            "interline_code": r[9],
        })
    return results


def record_rebooking(pnr_code: str, new_flight_numbers: str, partner_airline: str, ticket_no: str, bag_tag: str, voucher: str):
    """Log an interline rebooking transaction into the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Update PNR status
    cursor.execute(
        "UPDATE pnrs SET status = ? WHERE pnr_code = ?",
        (f"REBOOKED_VIA_{partner_airline.upper().replace(' ', '_')}", pnr_code.upper().strip()),
    )

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO rebookings (pnr_code, new_flight_numbers, partner_airline, interline_ticket_no, baggage_tag_id, voucher_details, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (pnr_code.upper().strip(), new_flight_numbers, partner_airline, ticket_no, bag_tag, voucher, now),
    )
    conn.commit()
    conn.close()


def get_rebooking_history(pnr_code: str):
    """Fetch rebooking history for a given PNR."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rebookings WHERE pnr_code = ? ORDER BY rebooking_id DESC", (pnr_code.upper().strip(),))
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        return None
    r = rows[0]
    return {
        "rebooking_id": r[0],
        "pnr_code": r[1],
        "new_flight_numbers": r[2],
        "partner_airline": r[3],
        "interline_ticket_no": r[4],
        "baggage_tag_id": r[5],
        "voucher_details": r[6],
        "timestamp": r[7],
    }


# Ensure database is set up when imported
_setup()
