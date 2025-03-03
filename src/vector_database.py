import sys
import os
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from src.logger import logging
from src.exception import CustomException
from langsmith import traceable
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
LANGCHAIN_API_KEY = os.environ.get("LANGCHAIN_API_KEY")
if not LANGCHAIN_API_KEY:
    logging.warning("LANGCHAIN_API_KEY is not set. LangSmith tracing might not work correctly.")

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY

# Step 1: Load raw PDF(s)
DATA_PATH = Path("data/")
logging.info("loading pdf files")

def load_pdf_files(data):
    try:
        loader = DirectoryLoader(data,
                                glob='*.pdf',
                                loader_cls=PyPDFLoader)
        
        documents=loader.load()
        return documents
    except Exception as e:
        logging.error("Error in loading PDF files")
        raise CustomException(e,sys)
    
documents=load_pdf_files(data=DATA_PATH)

def create_chunks(documents):
    """Splits the PDF content into smaller chunks."""
    logging.info("Creating chunks for PDF document")
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            add_start_index=True
        )
        text_chunks = text_splitter.split_documents(documents)
        logging.info(f"Successfully converted PDF into {len(text_chunks)} chunks")
        return text_chunks
    except Exception as e:
        logging.error("Error while creating chunks")
        raise CustomException(e, sys)
    
text_chunks=create_chunks(documents)
logging.info("Chunks created successfully")

@traceable
def get_embedding_model(model_name="deepseek-r1:1.5b"):
    """Returns the embedding model."""
    try:
        logging.info("Creating vector embeddings")
        return OllamaEmbeddings(model=model_name)
    except Exception as e:
        logging.error("Error in creating vector embeddings")
        raise CustomException(e, sys)
    
logging.info("Vector Embedding created successfully")    
embedding_model = get_embedding_model()

# Step 4: Store embeddings in FAISS
logging.info("Storing embedding in FAISS")

@traceable 
def store_embeddings(text_chunks, embedding_model, db_path):
    try:
        db = FAISS.from_documents(text_chunks, embedding_model)
        db.save_local(db_path)
        logging.info("Embeddings stored successfully")
    except Exception as e:
        logging.error("Error in storing embeddings")
        raise CustomException(e, sys)
    
DB_FAISS_PATH = Path("vectorstore/db_faiss")
store_embeddings(text_chunks, embedding_model, DB_FAISS_PATH)
