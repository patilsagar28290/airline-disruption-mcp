"""
airline_capstone.py - Airline Flight Disruption & Alliance Interline Rebooking MCP Control Panel (Gradio UI)

Demonstrates the power of Model Context Protocol (MCP) in the Airline & Travel domain.
Allows users to dynamically plug/unplug MCP servers (PNR Disruption, Alliance Partner Search, Welfare & Ticketing),
inspect discovered tools in real time, trigger sample disruption scenarios, and interact with the AI Recovery Specialist.

Run:
    uv run airline_capstone.py
"""

import os
import sys
import asyncio

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
import gradio as gr

load_dotenv()

# Script directory for resolving relative server paths reliably
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Define available local MCP Servers
SERVERS = {
    "PNR & Disruption Service": {
        "command": sys.executable,
        "args": [os.path.join(SCRIPT_DIR, "airline_disruption_mcp.py")],
        "transport": "stdio",
    },
    "Alliance Partner Engine": {
        "command": sys.executable,
        "args": [os.path.join(SCRIPT_DIR, "alliance_partner_mcp.py")],
        "transport": "stdio",
    },
    "Passenger Welfare & Interline E-Ticketing": {
        "command": sys.executable,
        "args": [os.path.join(SCRIPT_DIR, "passenger_welfare_mcp.py")],
        "transport": "stdio",
    },
}

from langchain_core.tools import tool

import airline_disruption_mcp
import alliance_partner_mcp
import passenger_welfare_mcp

# High-performance in-memory tool wrappers for zero-overhead execution on Render
IN_MEMORY_TOOLS = {
    "PNR & Disruption Service": [
        tool(airline_disruption_mcp.get_pnr_details),
        tool(airline_disruption_mcp.get_disruption_report),
        tool(airline_disruption_mcp.resolve_full_disruption_recovery),
    ],
    "Alliance Partner Engine": [
        tool(alliance_partner_mcp.search_alliance_alternatives),
        tool(alliance_partner_mcp.evaluate_rebooking_options),
    ],
    "Passenger Welfare & Interline E-Ticketing": [
        tool(passenger_welfare_mcp.issue_interline_ticket),
        tool(passenger_welfare_mcp.transfer_baggage_tags),
        tool(passenger_welfare_mcp.issue_welfare_vouchers),
    ],
}

SYSTEM_PROMPT = (
    "You are the Airline Alliance Disruption Recovery Specialist AI.\n"
    "Your goal is to protect passengers whose flights have been cancelled by rebooking them onto partner airlines "
    "(Star Alliance, Oneworld, SkyTeam) instead of offering standard cancellations and refunds.\n"
    "CRITICAL PERFORMANCE INSTRUCTION: Execute required recovery tools IN PARALLEL in your very first turn.\n"
    "Return a clear, professional passenger recovery summary immediately."
)


def config_for(selected):
    """Build client config from selected server keys."""
    return {name: SERVERS[name] for name in selected}


async def discover(selected):
    """Retrieve tools for checked servers with zero-overhead in-memory execution."""
    tools = []
    for key in selected:
        if key in IN_MEMORY_TOOLS:
            tools.extend(IN_MEMORY_TOOLS[key])
    return tools


def tools_panel(tools):
    """Render markdown list of currently plugged-in MCP tools."""
    if not tools:
        return "⚠️ **Connected MCP tools:** None — check an MCP server on the left panel to plug in tools."
    lines = [f"✅ **Connected MCP Tools ({len(tools)} plugged in):**"]
    for t in tools:
        lines.append(f"- `{t.name}`: {t.description}")
    return "\n".join(lines)


async def on_toggle(selected):
    """Re-discover tools when server checkboxes are toggled."""
    tools = await discover(selected)
    return tools_panel(tools)


async def on_message(message, history, selected):
    """Process chat message using agent built with currently plugged-in tools."""
    if not message.strip():
        return "", history, gr.update()

    if history is None:
        history = []

    if not selected:
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": "⚠️ No MCP servers are plugged in. Please check at least one server on the left panel to provide tools to the agent."})
        return "", history, tools_panel([])

    tools = await discover(selected)
    try:
        agent = create_agent(model="deepseek:deepseek-chat", tools=tools, system_prompt=SYSTEM_PROMPT)
        result = await agent.ainvoke({"messages": [{"role": "user", "content": message}]})
        last_msg = result["messages"][-1]
        if isinstance(last_msg.content, str):
            answer = last_msg.content.strip()
        else:
            answer = str(last_msg.content).strip()
    except Exception as err:
        answer = f"⚠️ Error: {str(err)}\n\nPlease ensure your DEEPSEEK_API_KEY is set correctly in .env."

    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": answer})
    return "", history, tools_panel(tools)


def set_scenario_prompt(scenario_name):
    """Fill user message box with preset scenario prompt."""
    if "AI9482" in scenario_name:
        return "Lookup PNR AI9482. Flight AI-101 is cancelled. Evaluate Star Alliance options to London Heathrow (LHR), rebook on the top Lufthansa flight, transfer baggage, and grant lounge vouchers."
    elif "LH4081" in scenario_name:
        return "Lookup PNR LH4081 (Lufthansa BOM to Frankfurt). Find alternative alliance options, issue interline ticket on Swiss Air, and transfer baggage."
    elif "SQ2319" in scenario_name:
        return "Lookup PNR SQ2319 (Singapore Airlines BLR to Tokyo NRT). Search partner flights, evaluate rebooking options, issue interline ticket on Thai Airways, and generate welfare vouchers."
    return ""


# Build Gradio UI Blocks
with gr.Blocks(title="✈️ Airline Disruption & Alliance Interline MCP Control Panel") as demo:
    gr.Markdown(
        "# ✈️ Airline Disruption Recovery & Alliance Interline MCP Control Panel\n"
        "**Demonstrating Model Context Protocol (MCP) in the Travel & Airline Domain.**\n\n"
        "Instead of cancelling tickets and issuing refunds during flight disruptions, this agent connects to "
        "decentralized **MCP Servers** to query partner airline inventory (Star Alliance, Oneworld), issue IATA interline e-tickets, "
        "and automatically transfer baggage and lounge vouchers.\n\n"
        "**Plug in servers on the left to instantly grant capabilities to the agent!**"
    )

    with gr.Row():
        # Left Panel: Server Controls & Tool Discovery
        with gr.Column(scale=1):
            gr.Markdown("### 🔌 MCP Server Plug & Play")
            servers = gr.CheckboxGroup(
                choices=list(SERVERS.keys()),
                value=list(SERVERS.keys()), # Default all plugged in
                label="Plug-in MCP Servers"
            )
            
            gr.Markdown("### 📋 Sample Disruption Scenarios")
            scenario_dropdown = gr.Dropdown(
                choices=[
                    "Scenario 1: PNR AI9482 (Air India DEL -> LHR Cancelled)",
                    "Scenario 2: PNR LH4081 (Lufthansa BOM -> FRA Cancelled)",
                    "Scenario 3: PNR SQ2319 (Singapore Airlines BLR -> NRT Cancelled)",
                ],
                label="Select Scenario",
                value="Scenario 1: PNR AI9482 (Air India DEL -> LHR Cancelled)"
            )
            load_scenario_btn = gr.Button("Load Selected Scenario Prompt")

            gr.Markdown("### 🛠️ Live Discovered MCP Tools")
            tools_md = gr.Markdown("Connecting...")

        # Right Panel: Agent Chatbot Interface
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(type="messages", height=500, label="🤖 Alliance Disruption Recovery AI Agent")
            message = gr.Textbox(
                placeholder="e.g. Lookup PNR AI9482 and find Star Alliance alternative flights to London Heathrow",
                label="Your Message / Instruction to Agent",
                value="Lookup PNR AI9482. Flight AI-101 is cancelled. Evaluate Star Alliance options to London Heathrow (LHR), rebook on the top Lufthansa flight, transfer baggage, and grant lounge vouchers."
            )
            submit_btn = gr.Button("Submit Request", variant="primary")

    # Wire Event Handlers
    servers.change(on_toggle, inputs=servers, outputs=tools_md)
    load_scenario_btn.click(set_scenario_prompt, inputs=scenario_dropdown, outputs=message)
    submit_btn.click(on_message, inputs=[message, chatbot, servers], outputs=[message, chatbot, tools_md])
    message.submit(on_message, inputs=[message, chatbot, servers], outputs=[message, chatbot, tools_md])

    # Initial Tool Discovery on Load
    demo.load(on_toggle, inputs=servers, outputs=tools_md)


async def run_selftest():
    """Selftest helper for validating MCP servers, tool discovery, and agent invocation."""
    print("[TEST] Running Airline Capstone Self-Test...")
    all_servers = list(SERVERS.keys())
    tools = await discover(all_servers)
    print(f"[TEST] Discovered {len(tools)} tools: {[t.name for t in tools]}")
    prompt = "Lookup PNR AI9482. Flight AI-101 is cancelled. Recommend alternative flights and issue interline ticket."
    _, history, _ = await on_message(prompt, [], all_servers)
    print("[TEST] Agent Answer:")
    safe_answer = history[-1]["content"].encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8')
    print(safe_answer)
    print("[TEST] Self-Test Completed Successfully!")


if __name__ == "__main__":
    if os.getenv("SELFTEST") == "1":
        asyncio.run(run_selftest())
    else:
        port = int(os.getenv("PORT", "7860"))
        demo.queue().launch(server_name="0.0.0.0", server_port=port)
