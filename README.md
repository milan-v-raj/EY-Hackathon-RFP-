# EY-Hackathon 
#  Agentic AI Workforce: Automated RFP Response System

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-orange)
![Gemini](https://img.shields.io/badge/AI-Gemini%202.5%20Flash-green)

**An autonomous multi-agent system that revolutionizes the B2B Procurement process.** This project deploys a squad of specialized AI Agents to autonomously find, analyze, and respond to complex Government Tenders (RFPs) with human-level accuracy and machine-level speed.

---

##  System Architecture

The system is built on a **Micro-Agent Architecture** orchestrated by **LangGraph**. It adheres to a strict "Separation of Concerns" where each agent has a specific domain of expertise.

### **The Agent Squad:**
1.  ** Sales Agent (Acquisition):** * Scans web portals (Selenium) or ingests local PDFs.
    * Qualifies leads and extracts metadata (Deadlines, Authority).
2.  ** Technical Agent (RAG Engine):**
    * Uses **Retrieval Augmented Generation (RAG)** to search a local Vector Database (ChromaDB) of product datasheets.
    * Matches RFP requirements to the exact internal SKU with a confidence score.
    * *Powered by: Google Gemini 2.5 Flash + HuggingFace Embeddings.*
3.  ** Pricing Agent (Semantic Logic):**
    * Uses a **Semantic Bridge (LLM)** to map technical descriptions to the internal Price List (SQLite).
    * Calculates precise Bill of Materials (BOM), Service Fees, and Margins.
4.  ** Master Agent (Synthesis):**
    * Compiles the outputs into a professional, legally compliant Bid Proposal.
5.  ** Human-in-the-Loop Cockpit:**
    * Allows engineering teams to review, refine, and provide feedback to agents before submission.

---

##  Installation & Setup

### Prerequisites
* Python 3.10 or higher
* Google Chrome (for Selenium scraping)
* A Google Cloud API Key (for Gemini)

### 1. Clone the Repository
```bash
git clone [https://github.com/your-username/rfp-agent-system.git](https://github.com/your-username/rfp-agent-system.git)
cd rfp-agent-system
