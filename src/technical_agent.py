# src/technical_agent.py
import os
import json
import streamlit as st
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

# @st.cache_resource ensures this function runs EXACTLY ONCE per session.
# It protects the model from being destroyed/recreated during 'Reiterate'.
@st.cache_resource
def get_shared_embeddings():
    print("🔌 Technical Agent: Loading Embedding Model (Cached via Streamlit)...")
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'} 
    )

class TechnicalAgent:
    def __init__(self):
        # 1. Load the model via the safe cached function
        self.embedding_fn = get_shared_embeddings()
        
        # 2. Initialize Vector DB with the cached embeddings
        self.db = Chroma(
            persist_directory="./data/vectordb", 
            embedding_function=self.embedding_fn
        )
        
        if "GOOGLE_API_KEY" not in os.environ:
            raise ValueError("GOOGLE_API_KEY missing")
            
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0
        )

    def analyze_specs(self, rfp_snippet, feedback=""):
        print("⚙️ Technical Agent: Analyzing multiple line items...")
        
        # Retrieval
        results = self.db.similarity_search(rfp_snippet, k=6)
        context_text = "\n\n".join([doc.page_content for doc in results])
        
        # Prompt
        prompt_text = """
            You are a Technical Specification Engineer.
            
            TASK: Match each item in the RFP Requirement to the EXACT 'Catalogue Number' or 'Basic Code' found in the Available Catalogue.
            
            RFP REQUIREMENTS:
            {rfp_req}
            
            AVAILABLE CATALOGUE (Source of Truth):
            {context}
            
            ---------------------------------------------------
            TEAM FEEDBACK (Must Prioritize):
            {feedback}
            ---------------------------------------------------
            
            INSTRUCTIONS:
            1. Identify every distinct item requested in the RFP.
            2. Search the catalogue text for the exact "Catalogue Number", "Basic Code", or "Item Code".
            3. If no code is found, use the most specific product name available.
            4. Extract the Quantity requested for each item.
            
            OUTPUT FORMAT (Strict JSON List):
            [
                {{
                    "rfp_item_name": "Name from RFP (e.g. 4.0 sqmm Cable)",
                    "selected_sku": "EXACT_CODE_OR_NAME", 
                    "quantity": 5000,
                    "confidence": 95,
                    "reason": "Found exact match for 4.0 sqmm FR PVC..."
                }}
            ]
            """
            
        prompt = PromptTemplate(
            template=prompt_text,
            input_variables=["rfp_req", "context", "feedback"]
        )
        
        chain = prompt | self.llm
        
        response = chain.invoke({
            "rfp_req": rfp_snippet, 
            "context": context_text,
            "feedback": feedback if feedback else "None"
        })
        
        return response.content