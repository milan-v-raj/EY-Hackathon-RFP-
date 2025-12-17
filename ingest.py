# ingest.py
import os
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# 1. Load PDFs
DATA_PATH = "./data/pdfs"
DB_PATH = "./data/vectordb"

print("Loading PDFs...")
loader = PyPDFDirectoryLoader(DATA_PATH)
documents = loader.load()

# 2. Split Text (Chunks)
# We split text so the AI can find specific specs without reading the whole page
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
chunks = text_splitter.split_documents(documents)
print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

# 3. Create Vector DB
# Using a local CPU model for embeddings (Free & Fast)
print("Creating Embeddings (this may take a minute)...")
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Persist to disk
db = Chroma.from_documents(
    documents=chunks, 
    embedding=embedding_model, 
    persist_directory=DB_PATH
)

print(f"Vector Database created at {DB_PATH}")