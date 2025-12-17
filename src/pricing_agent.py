# src/pricing_agent.py
import sqlite3
import pandas as pd
import json
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

class PricingAgent:
    def __init__(self, db_path="pricing_data.db"):
        self.db_path = db_path
        
        # Initialize LLM for the "Semantic Bridge"
        if "GOOGLE_API_KEY" not in os.environ:
            raise ValueError("GOOGLE_API_KEY missing")
            
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0
        )

    def _get_all_products_as_text(self):
        """Fetches the entire catalog to give context to the LLM."""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql("SELECT sku_id, description, unit_price FROM material_pricing", conn)
        conn.close()
        
        # Convert to a readable string format for the prompt
        # Format: "SKU_ID | Description | Price"
        catalog_text = ""
        for _, row in df.iterrows():
            catalog_text += f"- SKU: {row['sku_id']} | Desc: {row['description']} | Price: {row['unit_price']}\n"
        return catalog_text

    def calculate_quote(self, matched_items, testing_reqs=""):
        print(f"💰 Pricing Agent: Semantic Matching for {len(matched_items)} items...")
        
        # 1. Get the Full Catalog context
        catalog_context = self._get_all_products_as_text()
        
        # 2. Construct the input list for the prompt
        input_items_str = ""
        for i, item in enumerate(matched_items, 1):
            name = item.get('rfp_item_name', 'Unknown')
            tech_desc = item.get('selected_sku', 'Generic Description')
            input_items_str += f"Item {i}: Request='{name}', Tech_Match='{tech_desc}'\n"

        # 3. THE SEMANTIC BRIDGE PROMPT
        prompt = PromptTemplate(
            template="""
            You are a Commercial Estimator. match technical requests to our Approved Price List.
            
            OUR PRICE LIST (Database):
            {catalog}
            
            REQUESTED ITEMS (From Technical Team):
            {requests}
            
            INSTRUCTIONS:
            1. For each Requested Item, find the BEST matching SKU from the Price List.
            2. Use the Technical Match description to guide you, but pick the exact SKU from the Price List.
            3. If the description is "4.0 sqmm", match it to the corresponding 4.0mm SKU (e.g., WSFFDN...A14X07).
            4. If no good match exists, select the closest alternative or a Generic fallback.
            
            OUTPUT FORMAT (Strict JSON List of objects):
            [
                {{
                    "rfp_item_index": 1,
                    "matched_sku_id": "WSFFDN...A14X07",
                    "matched_description": "Standard Home Shield 4.0 sq.mm...",
                    "unit_price": 72.00
                }}
            ]
            """,
            input_variables=["catalog", "requests"]
        )
        
        # 4. Invoke LLM
        chain = prompt | self.llm
        try:
            response = chain.invoke({
                "catalog": catalog_context,
                "requests": input_items_str
            })
            
            # Clean and Parse JSON
            clean_json = response.content.replace('```json', '').replace('```', '').strip()
            pricing_matches = json.loads(clean_json)
            
        except Exception as e:
            print(f"   ⚠️ Semantic Pricing Failed: {e}. Reverting to fallback.")
            pricing_matches = []

        # 5. Calculate Finals
        line_items = []
        total_material_cost = 0
        
        # Map the LLM results back to the quantities
        for i, item in enumerate(matched_items, 1):
            qty = item.get('quantity', 1000)
            
            # Find the match for this index
            match = next((m for m in pricing_matches if m.get('rfp_item_index') == i), None)
            
            if match:
                sku = match['matched_sku_id']
                desc = match['matched_description']
                price = match['unit_price']
            else:
                # Fallback if LLM missed it
                sku = "FALLBACK"
                desc = item.get('selected_sku', 'Generic')
                price = 100.0 # Safe default
            
            subtotal = price * qty
            total_material_cost += subtotal
            
            line_items.append({
                "description": desc,
                "unit_price": price,
                "quantity": qty,
                "subtotal": subtotal
            })

        # 6. Services & Totals
        service_cost = 0
        if "High Voltage" in testing_reqs: service_cost += 2500.0
        if "Flammability" in testing_reqs: service_cost += 4500.0
        if service_cost == 0: service_cost = 5000.0 

        base_total = total_material_cost + service_cost
        margin_multiplier = 1.25
        final_total = base_total * margin_multiplier
        
        return {
            "line_items": line_items,
            "service_fees": service_cost,
            "base_total": base_total,
            "margin_amount": final_total - base_total,
            "final_total_price": final_total
        }