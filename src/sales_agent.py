# src/sales_agent.py
import json
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

class SalesAgent:
    def __init__(self, mock_data_path="data/mock_rfp.json"):
        self.mock_data_path = mock_data_path

    def _get_browser(self):
        """Helper to open a visible browser."""
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # --- (Visual Simulation) ---
    def run_visual_simulation(self):
        print(f"   🎬 Sales Agent: Starting Visual Simulation...")
        
        target_url = "https://etenders.gov.in/eprocure/app"
        
        driver = self._get_browser()
        try:
            driver.get(target_url)
            time.sleep(3) 
            
            
            driver.execute_script("window.scrollTo(0, 500);")
            time.sleep(1)
            print("   ✅ Simulation: Connection established. 'Scraping' data...")
            driver.quit()
            
            # Return safe Mock Data
            return self.load_mock_data()
        except Exception as e:
            if driver: driver.quit()
            print(f"   ❌ Simulation Error: {e}")
            return self.load_mock_data()

    # --- FEATURE: REAL SCRAPE (Custom URL) ---
    def run_real_scrape(self, url):
        print(f"   🕷️ Sales Agent: Real Scrape on {url}...")
        driver = self._get_browser()
        try:
            driver.get(url)
            time.sleep(4) # Wait for JS
            
            page_title = driver.title
            # Grab body text (limit to 3000 chars for LLM safety)
            body_text = driver.find_element(By.TAG_NAME, "body").text[:3000]
            
            print(f"   ✅ Real Scrape Successful: {page_title[:30]}...")
            driver.quit()
            
            return {
                "rfp_id": "REAL_WEB_" + str(int(time.time())),
                "title": page_title,
                "authority": "Custom Web Source",
                "deadline": "See Text Details",
                "source_url": url,
                "raw_text": body_text
            }
        except Exception as e:
            if driver: driver.quit()
            return {"error": f"Scrape failed: {str(e)}", "raw_text": ""}

    # --- FEATURE 3: PDF EXTRACTION ---
    def run_pdf_extraction(self, file_path):
        print(f"   📂 Sales Agent: Processing PDF {file_path}...")
        try:
            # Import here to avoid dependency errors if user lacks libraries
            from src.pdf_sales_agent import LocalPDFSalesAgent
            
            if not os.path.exists(file_path):
                return {"error": "PDF file not found."}
                
            agent = LocalPDFSalesAgent(file_path)
            return agent.extract_rfp_data()
        except Exception as e:
            return {"error": f"PDF Extraction failed: {str(e)}"}

    def load_mock_data(self):
        """Helper to load the fake JSON."""
        try:
            if not os.path.exists(self.mock_data_path):
                return {"title": "Error: mock_rfp.json missing", "raw_text": "Supply of 4.0 sq.mm Cable"}
            with open(self.mock_data_path, 'r') as f:
                return json.load(f)
        except:
            return {}