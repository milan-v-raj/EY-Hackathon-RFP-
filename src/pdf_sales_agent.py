# src/pdf_sales_agent.py
import os
import time
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

load_dotenv()

class LocalPDFSalesAgent:
    def __init__(self, file_path):
        self.file_path = file_path
        
        if "GOOGLE_API_KEY" not in os.environ:
            raise ValueError("GOOGLE_API_KEY not found in .env file")
            
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0
        )

    def extract_rfp_data(self):
        """
        Reads a local PDF and uses LLM to extract structured RFP details.
        """
        print(f"\n📂 PDF Agent: Reading file '{self.file_path}'...")
        
        # 1. LOAD PDF
        try:
            loader = PyPDFLoader(self.file_path)
            pages = loader.load()
            full_text = "\n".join([page.page_content for page in pages])
            print(f"  Loaded {len(pages)} pages. Text length: {len(full_text)} characters.")
        except Exception as e:
            return {"error": f"Failed to read PDF: {str(e)}"}

        # 2. DEFINE EXTRACTION PROMPT
        prompt = PromptTemplate(
            template="""
            You are an expert RFP Analyst. Your job is to extract key details from a Tender Document.
            
            SOURCE DOCUMENT TEXT:
            {text}
            
            ----------------------------------------------------------------
            INSTRUCTIONS:
            1. Identify the 'Tender Title' or 'Name of Work'.
            2. Identify the 'Issuing Authority' (Organization Name).
            3. Identify the 'Bid Submission Deadline' (Date). If not found, output "Unknown".
            4. Extract the 'Technical Specifications' relevant to Cables/Wires (Voltage, Core, Size, Type, Quantity). 
               Summarize the specs clearly in a text block.
            
            OUTPUT FORMAT (JSON ONLY, No Markdown):
            {{
                "title": "...",
                "authority": "...",
                "deadline": "YYYY-MM-DD",
                "technical_summary": "..."
            }}
            """,
            input_variables=["text"]
        )

        # 3. RUN EXTRACTION CHAIN
        print("  PDF Agent: AI is analyzing document structure...")
        chain = prompt | self.llm
        
        
        response = chain.invoke({"text": full_text[:40000]}) 
        
        # 4. PARSE & FORMAT FOR MASTER AGENT
        try:
            # Clean JSON markdown
            clean_json = response.content.replace('```json', '').replace('```', '').strip()
            extracted_data = json.loads(clean_json)
            
            # Handle deadlines
            deadline = extracted_data.get("deadline", "")
            if "Unknown" in deadline or not deadline:
                deadline = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

            # Construct the final object compatible with Master Agent
            rfp_data = {
                "rfp_id": "LOCAL_PDF_" + str(int(time.time())),
                "title": extracted_data.get("title", "Unknown Title"),
                "authority": extracted_data.get("authority", "Unknown Authority"),
                "deadline": deadline,
                "source_url": f"Local File: {os.path.basename(self.file_path)}",
                "raw_text": extracted_data.get("technical_summary", "")
            }
            
            print("    Extraction Complete.")
            return rfp_data

        except json.JSONDecodeError:
            print("    Error: AI output was not valid JSON.")
            return {"error": "Parsing Failed", "raw_response": response.content}

if __name__ == "__main__":
    # Test with your specific file
    test_pdf = "specifications_of_copper_cables_2024-01-22-15-20-17_380f50986d0879644a51cbad3392c672.pdf" 
    if os.path.exists(test_pdf):
        agent = LocalPDFSalesAgent(test_pdf)
        result = agent.extract_rfp_data()
        print("\n--- FINAL EXTRACTED OUTPUT ---")
        print(json.dumps(result, indent=2))
    else:
        print(f"File {test_pdf} not found.")