
```markdown
#  Agentic AI Workforce: Automated RFP Response System

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-orange)
![Gemini](https://img.shields.io/badge/AI-Gemini%201.5%20Flash-green)

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
    * *Powered by: Google Gemini 1.5 Flash + HuggingFace Embeddings.*
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

```

### 2. Set Up Virtual Environment

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

```

### 3. Install Dependencies

```bash
pip install -r requirements.txt

```

### 4. Configure Secrets

Create a `.env` file in the root directory and add your API key:

```env
GOOGLE_API_KEY=your_actual_api_key_here

```

---

##  Database Initialization

Before running the app, you must build the "Knowledge Bases" for the agents.

**1. Build the Pricing Database (SQL)**
Creates the SQLite database with products and service costs.

```bash
python setup_sql.py

```

**2. Build the Technical Knowledge Base (Vector DB)**
Ingests PDF datasheets from `data/pdfs` and creates embeddings.
*(Make sure you have PDFs in the `data/pdfs` folder first)*

```bash
python ingest.py

```

---

## 🚀 Running the Application

Launch the **Streamlit Cockpit**:

```bash
streamlit run app.py

```

### **How to Use the Dashboard:**

1. **Select Input Channel:** Choose "Demo Simulation", "Live Web Scraper", or "PDF Upload" from the sidebar.
2. **Watch the Agents Work:** The progress bar will track the autonomous workflow (Sales -> Technical -> Pricing -> Synthesis).
3. **Review the Draft:** See the generated proposal in the main window.
4. **Human Feedback Loop:** * Scroll to the "Team Supervision" box.
* Type a correction (e.g., *"Item 1 needs Fire Survival cable"*).
* Click **"Reiterate"** to force the agents to re-think and update the quote.


5. **Admin Panel:** Use the sidebar to add new products to the catalogue instantly.

---

##  Project Structure

```text
├── src/
│   ├── sales_agent.py       # Web Scraping & PDF Ingestion logic
│   ├── technical_agent.py   # RAG Engine & Vector Search
│   ├── pricing_agent.py     # SQL Logic & Semantic Pricing Bridge
│   ├── master_agent.py      # LangGraph State Machine & Orchestrator
│   ├── product_manager.py   # Admin tool for adding new products
│   └── pdf_sales_agent.py   # Helper for PDF parsing
├── data/
│   ├── pdfs/                # Raw Datasheets for ingestion
│   ├── vectordb/            # ChromeDB storage (Auto-generated)
│   └── mock_rfp.json        # Mock data for safe demos
├── app.py                   # Main Streamlit Frontend
├── ingest.py                # Script to build Vector DB
├── setup_sql.py             # Script to build SQL Pricing DB
├── requirements.txt         # Project dependencies
└── .env                     # API Keys (Not committed)

```

---

##  Future Roadmap

* **Enterprise Deployment:** Containerize agents using Docker & Kubernetes.
* **Feedback Learning:** Implement a reinforcement learning loop where human edits retrain the vector matching model.
* **Multi-Modal Analysis:** Enable agents to read engineering drawings/blueprints (CAD/Images) directly.

---

### License

This project is licensed under the MIT License.

```


```
