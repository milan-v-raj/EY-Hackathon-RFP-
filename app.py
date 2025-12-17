# app.py
import streamlit as st
import time
import os
from src.master_agent import app as agent_workflow
from src.sales_agent import SalesAgent

# Page Config
st.set_page_config(page_title="AI RFP Cockpit", layout="wide")
st.title("Agentic AI Workforce: Automated RFP Response")

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("1. Acquisition Channel")
    
    # FEATURE 1: SIMULATION
    st.subheader("Option A: Demo Simulation")
    if st.button(" Start Mock Scrape"):
        st.session_state['mode'] = 'simulation'
        st.session_state['run_pipeline'] = True
        # Clear previous feedback on new run
        st.session_state['tech_feedback_input'] = ""

    st.divider()

    # FEATURE 2: REAL WEB SCRAPE
    st.subheader("Option B: Live Web Scraper")
    custom_url = st.text_input("Enter Tender Portal URL", "https://gem.gov.in")
    if st.button(" Scrape URL"):
        st.session_state['mode'] = 'real_web'
        st.session_state['target_url'] = custom_url
        st.session_state['run_pipeline'] = True
        st.session_state['tech_feedback_input'] = ""

    st.divider()

    # FEATURE 3: PDF UPLOAD
    st.subheader("Option C: PDF Upload")
    uploaded_file = st.file_uploader("Upload RFP Document", type=['pdf'])
    if uploaded_file and st.button(" Extract from PDF"):
        # Save temp file
        with open("temp_rfp.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.session_state['mode'] = 'pdf'
        st.session_state['pdf_path'] = "temp_rfp.pdf"
        st.session_state['run_pipeline'] = True
        st.session_state['tech_feedback_input'] = ""

# --- MAIN EXECUTION LOGIC ---
if not st.session_state.get('run_pipeline'):
    st.info("Select an option in the sidebar to begin the RFP response process.")

else:
    # 1. RUN SALES AGENT (Acquisition Phase)
    st.subheader(" Phase 1: Acquisition & Qualification")
    status_box = st.empty()
    
    # Initialize RFP Data container in session state to persist between reruns
    if 'rfp_data_cache' not in st.session_state:
        st.session_state['rfp_data_cache'] = {}

    # Only run the heavy scraping ONCE, unless we switched modes
    if not st.session_state['rfp_data_cache'] or st.session_state.get('trigger_new_scrape'):
        sales_agent = SalesAgent()
        rfp_data = {}

        if st.session_state['mode'] == 'simulation':
            status_box.info(" Mode: Visual Simulation (Mock Data)...")
            rfp_data = sales_agent.run_visual_simulation()
            
        elif st.session_state['mode'] == 'real_web':
            status_box.info(f" Mode: Real Scraping on {st.session_state['target_url']}...")
            rfp_data = sales_agent.run_real_scrape(st.session_state['target_url'])
            
        elif st.session_state['mode'] == 'pdf':
            status_box.info(" Mode: PDF Extraction...")
            rfp_data = sales_agent.run_pdf_extraction(st.session_state['pdf_path'])
        
        # Save to cache
        st.session_state['rfp_data_cache'] = rfp_data
        st.session_state['trigger_new_scrape'] = False
    
    # Load from cache
    rfp_data = st.session_state['rfp_data_cache']

    # Show result of Sales Agent
    if "error" in rfp_data:
        st.error(f"Acquisition Failed: {rfp_data['error']}")
    else:
        st.success(" RFP Identified & Qualified")
        with st.expander(" View Extracted RFP Data", expanded=False):
            st.json(rfp_data)

        # 2. RUN MASTER AGENT (The rest of the pipeline)
        st.subheader(" Phase 2: Autonomous Processing")
        
        # --- HUMAN IN THE LOOP INPUTS ---
        # Retrieve any stored feedback from session state
        user_feedback = st.session_state.get('tech_feedback_input', "")
        
        # We pass the 'rfp_data' AND 'technical_feedback' to the workflow
        inputs = {
            "rfp_url": "SKIP", 
            "rfp_data": rfp_data,
            "technical_feedback": user_feedback
        }
        
        final_state = None
        step_count = 0
        progress_bar = st.progress(0)
        
        # Container for the workflow output so we can refresh it easily
        with st.container():
            try:
                for output in agent_workflow.stream(inputs):
                    for key, value in output.items():
                        step_count += 25
                        if step_count > 100: step_count = 100
                        progress_bar.progress(step_count)
                        
                        if key == "sales":
                            pass 
                        
                        elif key == "technical":
                            st.write("🔧 **Technical Agent:** Analyzing specs against product catalog...")
                            with st.expander("View Technical Analysis", expanded=True):
                                items = value.get('selected_sku', [])
                                if isinstance(items, list):
                                    for i, item in enumerate(items, 1):
                                        st.markdown(f"#### Item {i}: {item.get('rfp_item_name', 'Unknown')}")
                                        
                                        # --- NEW: CONFIDENCE SCORE VISUALIZATION ---
                                        confidence = item.get('confidence', 0)
                                        # Create columns for layout
                                        c1, c2 = st.columns([3, 1])
                                        with c1:
                                            st.info(f"**Matched SKU:** {item.get('selected_sku')}")
                                        with c2:
                                            # Color code the metric
                                            delta_color = "normal"
                                            if confidence > 85: delta_color = "normal" # Greenish usually
                                            elif confidence < 50: delta_color = "inverse" # Reddish
                                            
                                            st.metric("Confidence", f"{confidence}%", delta_color=delta_color)
                                        
                                        # Visual Progress Bar
                                        st.progress(min(confidence, 100) / 100)
                                        
                                        st.caption(f"**Reasoning:** {item.get('reason')}")
                                        st.divider()
                                else:
                                    st.write(items) # Fallback
                                
                        elif key == "pricing":
                            st.write(" **Pricing Agent:** Calculating BOM and margins...")
                            with st.expander("View Cost Breakdown"):
                                quote = value.get('final_quote', {})
                                st.write(f"**Base Total:** {quote.get('base_total', 0):,.2f}")
                                st.write(f"**Final Total:** {quote.get('final_total_price', 0):,.2f}")
                                st.table(quote.get('line_items', []))
                                
                        elif key == "synthesis":
                            st.write(" **Master Agent:** Compiling final proposal...")
                            final_state = value

                progress_bar.progress(100)

            except Exception as e:
                st.error(f"Workflow Error: {e}")

        # --- FEEDBACK BOX ---
        st.warning(" Team Supervision Required")
        col_fb1, col_fb2 = st.columns([3, 1])
        
        with col_fb1:
            fb_text = st.text_area(
                "Give suggestions to Technical Agent (e.g., 'Item 1 requires Fire Survival cable'):", 
                value=st.session_state.get('tech_feedback_input', ""),
                key="feedback_box_ui"
            )
        
        with col_fb2:
            st.write("") # Spacer
            st.write("") # Spacer
            if st.button("🔄 Reiterate / Refine"):
                # Save feedback and rerun the app
                st.session_state['tech_feedback_input'] = fb_text
                # Don't trigger new scrape, just re-run logic
                st.rerun()

        # 3. FINAL OUTPUT
        st.divider()
        st.subheader(" Final Draft for Review")
        if final_state:
            draft = final_state.get('draft_response', 'Error')
            st.text_area("Draft Proposal", draft, height=450)
            