# ✈️ Airline Disruption Recovery & Alliance Interline MCP System

An end-to-end **Model Context Protocol (MCP)** demonstration for the **Travel & Airline Domain**.

Instead of cancelling flight bookings and issuing cash refunds during flight disruptions (such as aircraft technical snags, weather events, or strikes), this system leverages decentralized **MCP Tool Servers** to query partner airline inventory (Star Alliance, Oneworld, SkyTeam), issue IATA interline electronic tickets (IATA Res 735d), update automated baggage transfer tags, and grant lounge/hotel vouchers.

---

## 🌟 Key Features

1. **PNR & Disruption Service (`airline_disruption_mcp.py`)**: FastMCP server exposing PNR details and official flight disruption logs.
2. **Alliance Partner Engine (`alliance_partner_mcp.py`)**: FastMCP server searching seat inventory across Star Alliance, Oneworld, and SkyTeam partners (Lufthansa, Swiss Air, Singapore Airlines, Thai Airways, ANA, Qatar Airways) and ranking optimal itineraries.
3. **Passenger Welfare & Interline E-Ticketing (`passenger_welfare_mcp.py`)**: FastMCP server re-issuing $0 interline e-tickets, transferring IATA baggage tags, and issuing Star Alliance lounge/hotel vouchers.
4. **Interactive Dark-Themed Gradio Control Panel (`airline_capstone.py`)**: Web UI allowing users to dynamically plug/unplug MCP servers, inspect discovered tools in real time, trigger preset disruption scenarios, and chat with the AI Recovery Agent.

---

## 📁 Repository Structure

```
├── airline_db.py              # SQLite database layer for PNRs & alliance inventory
├── airline_disruption_mcp.py  # FastMCP Server 1: PNR & Disruption Service
├── alliance_partner_mcp.py    # FastMCP Server 2: Alliance Partner Search & Ranking
├── passenger_welfare_mcp.py   # FastMCP Server 3: Interline E-Ticketing & Welfare Vouchers
├── airline_capstone.py        # Dark-Themed Gradio Control Panel UI & LangChain Agent
├── requirements.txt           # Python dependencies for local & cloud hosting
└── .env.example               # Environment variable template
```

---

## 🚀 Quick Start (Local)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file from `.env.example`:
```bash
DEEPSEEK_API_KEY=your_actual_deepseek_api_key
```

### 3. Launch the Control Panel
```bash
python airline_capstone.py
```
Open `http://127.0.0.1:7860` in your browser.

---

## ☁️ Deploying to Render (render.com)

1. Connect this GitHub repository to [Render.com](https://render.com/).
2. Select **New Web Service**.
3. Set **Build Command**: `pip install -r requirements.txt`
4. Set **Start Command**: `python airline_capstone.py`
5. Add Environment Variable: `DEEPSEEK_API_KEY`
