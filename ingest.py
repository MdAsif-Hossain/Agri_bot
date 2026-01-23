import os
import shutil
from langchain_community.document_loaders import PyPDFDirectoryLoader
# FIXED IMPORT: Using the new library name
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# --- CONFIGURATION ---
DATA_PATH = "data/pdfs"
DB_PATH = "chroma_db"

def create_vector_db():
    print("🚜 Starting Data Ingestion...")

    # 1. Load PDFs
    if not os.path.exists(DATA_PATH):
        print(f"❌ Error: '{DATA_PATH}' folder missing!")
        print("   Please create a folder named 'pdfs' inside 'data' and put your PDF there.")
        return
        
    loader = PyPDFDirectoryLoader(DATA_PATH)
    documents = loader.load()
    
    if len(documents) == 0:
        print("⚠️ No PDFs found. Please add a PDF to data/pdfs/")
        return
    print(f"   Loaded {len(documents)} pages.")

    # 2. Split Text
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100
    )
    chunks = text_splitter.split_documents(documents)
    print(f"   Created {len(chunks)} chunks.")

    # 3. Embeddings
    print("🧠 Loading Embeddings...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # 4. Save to ChromaDB
    if os.path.exists(DB_PATH):
        try:
            shutil.rmtree(DB_PATH) # Clean cleanup
        except Exception as e:
            print(f"⚠️ Could not delete old DB (might be in use). Continuing...")

    print("💾 Saving Database...")
    Chroma.from_documents(
        documents=chunks, 
        embedding=embeddings,
        persist_directory=DB_PATH
    )
    print(f"✅ Success! Database saved to '{DB_PATH}'.")

if __name__ == "__main__":
    create_vector_db()