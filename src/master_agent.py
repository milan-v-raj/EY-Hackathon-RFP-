# src/master_agent.py
import json
import re
import os
import time
from typing import TypedDict, List
from langgraph.graph import StateGraph, END

# Import your agents
from src.sales_agent import SalesAgent
from src.technical_agent import TechnicalAgent
from src.pricing_agent import PricingAgent

def clean_json_output(llm_response_str):
    """
    Cleans the string response from the LLM to ensure it's valid JSON.
    """
    clean_str = re.sub(r'```json\s*', '', llm_response_str)
    clean_str = re.sub(r'```', '', clean_str)
    return clean_str.strip()

# 1. Define the Shared State
class AgentState(TypedDict):
    rfp_url: str
    rfp_data: dict          
    technical_reqs: str     
    testing_reqs: str       
    selected_sku: list      
    final_quote: dict       
    draft_response: str
    technical_feedback: str  

# 2. Define the Nodes

def sales_node(state: AgentState):
    """Step 1: Find the RFP"""
    print("--- SALES NODE ---")
    
    # Check if data was pre-loaded (PDF Mode)
    existing_data = state.get('rfp_data')
    if existing_data and isinstance(existing_data, dict) and "title" in existing_data:
        print(f"   ✅ Using Pre-loaded Data: {existing_data.get('title')}")
        return {"rfp_data": existing_data}

    # Otherwise run Web Scraper
    print("   🌐 Running Web Scraper...")
    backup_file = "specifications_of_copper_cables_2024-01-22-15-20-17_380f50986d0879644a51cbad3392c672.pdf"
    
    agent = SalesAgent(pdf_backup_path=backup_file if os.path.exists(backup_file) else None)
    rfp_data = agent.scrape_portal(state.get('rfp_url'))
    
    if not isinstance(rfp_data, dict):
        rfp_data = {"error": "Invalid data format from Sales Agent"}
        
    return {"rfp_data": rfp_data}

def decomposition_node(state: AgentState):
    """Step 2: Split Context"""
    print("--- DECOMPOSITION NODE ---")
    rfp = state.get('rfp_data', {})
    raw_text = rfp.get('raw_text', '')
    if not raw_text:
        raw_text = f"Title: {rfp.get('title', 'Unknown RFP')}"
    return {
        "technical_reqs": raw_text, 
        "testing_reqs": raw_text
    }

def technical_node(state: AgentState):
    """Step 3: Technical Agent matches MULTIPLE SKUs"""
    print("--- TECHNICAL NODE ---")
    agent = TechnicalAgent()
    reqs = state.get('technical_reqs', "")
    
    # GET FEEDBACK FROM STATE
    user_feedback = state.get('technical_feedback', "")
    
    # PASS FEEDBACK TO AGENT
    response_str = agent.analyze_specs(reqs, feedback=user_feedback)
    
    try:
        clean_str = clean_json_output(response_str)
        sku_data = json.loads(clean_str)
        if isinstance(sku_data, dict):
            sku_data = [sku_data]
    except (json.JSONDecodeError, TypeError):
        print("⚠️ Warning: Parsing Error in Technical Node.")
        sku_data = [{"selected_sku": "Generic Cable", "confidence": 0, "reason": "Error"}]

    return {"selected_sku": sku_data}

def pricing_node(state: AgentState):
    """Step 4: Pricing Agent calculates cost for LIST"""
    print("--- PRICING NODE ---")
    agent = PricingAgent()
    
    # Get list of matched items
    items = state.get('selected_sku', [])
    testing_reqs = state.get('testing_reqs', '')
    
    # Use the NEW calculate_quote method that handles lists
    quote = agent.calculate_quote(items, testing_reqs)
    return {"final_quote": quote}

def synthesis_node(state: AgentState):
    """Step 5: Write the Draft (Now with Confidence Scores)"""
    print("--- SYNTHESIS NODE ---")
    quote = state.get('final_quote', {})
    sku_list = state.get('selected_sku', []) 
    rfp = state.get('rfp_data', {})
    
    # --- 1. Generate Technical Summary Text (Looping through list) ---
    tech_summary = ""
    if isinstance(sku_list, list):
        for i, item in enumerate(sku_list, 1):
            name = item.get('rfp_item_name', 'Item')
            match = item.get('selected_sku', 'Unknown')
            reason = item.get('reason', 'N/A')
            # NEW: Extract Confidence
            conf = item.get('confidence', 0)
            
            tech_summary += f"{i}. Request: {name}\n   Match:   {match}\n   Confidence: {conf}%\n   Reason:  {reason}\n\n"
    else:
        tech_summary = "Technical data format error."

    # --- 2. Generate Pricing Table Rows ---
    table_rows = ""
    line_items = quote.get('line_items', [])
    
    for i, item in enumerate(line_items, 1):
        desc = item.get('description', 'Item')[:35]
        u_price = item.get('unit_price', 0)
        qty = item.get('quantity', 0)
        sub = item.get('subtotal', 0)
        
        row = f"| {i}. {desc:<35} | {u_price:>10,.2f} | {qty:>6} | {sub:>14,.2f} |\n"
        table_rows += row

    # --- 3. Construct Final Draft ---
    draft = f"""
    OFFICIAL BID PROPOSAL
    ================================================================================
    To:     {rfp.get('authority', 'Procurement Officer')}
    Ref:    {rfp.get('title', 'Tender Response')}
    Date:   {time.strftime("%d-%B-%Y")}
    ================================================================================

    1. EXECUTIVE SUMMARY
    --------------------
    We are pleased to submit our proposal for the following items based on your 
    technical requirements.

    2. TECHNICAL SOLUTION & COMPLIANCE
    ----------------------------------
    {tech_summary}

    3. COMMERCIAL PROPOSAL
    ----------------------
    Currency: INR (Indian Rupee)

    | Item Description                        | Unit Price |    Qty |       Subtotal |
    |-----------------------------------------|------------|--------|----------------|
    {table_rows}| {len(line_items)+1}. Testing & Logistics Services        |   Flat Fee |      1 | {quote.get('service_fees', 0):>14,.2f} |
    |-----------------------------------------|------------|--------|----------------|
    |    Net Total (Before Overheads)         |            |        | {quote.get('base_total', 0):>14,.2f} |
    |    Operational Overheads & Margin       |            |        | {quote.get('margin_amount', 0):>14,.2f} |
    |=========================================|============|========|================|
    |    GRAND TOTAL PROJECT VALUE            |            |        | {quote.get('final_total_price', 0):>14,.2f} |
    |=========================================|============|========|================|

    Sincerely,
    Agentic AI Sales Team
    """
    return {"draft_response": draft}

# 3. Build the Graph
workflow = StateGraph(AgentState)

workflow.add_node("sales", sales_node)
workflow.add_node("decompose", decomposition_node)
workflow.add_node("technical", technical_node)
workflow.add_node("pricing", pricing_node)
workflow.add_node("synthesis", synthesis_node)

# 4. Connect
workflow.set_entry_point("sales")
workflow.add_edge("sales", "decompose")
workflow.add_edge("decompose", "technical")
workflow.add_edge("technical", "pricing")
workflow.add_edge("pricing", "synthesis")
workflow.add_edge("synthesis", END)

app = workflow.compile()