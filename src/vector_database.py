import sys
import os
from pathlib import Path
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from src.logger import logging
from src.exception import CustomException

# Step 1: Define the PDFs directory
pdfs_directory = Path("data")
pdfs_directory.mkdir(parents=True, exist_ok=True)  # Ensure directory exists

def upload_pdf(file):
    """Uploads a PDF file to the 'data' directory."""
    logging.info("Uploading PDF file")
    try:
        file_path = pdfs_directory / file.name  # Correctly join path
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
        logging.info(f"File uploaded successfully: {file_path}")
        return file_path
    except Exception as e:
        logging.error("Error in uploading PDF file")
        raise CustomException(e, sys)

def load_pdf(file_path):
    """Loads a PDF file if it exists."""
    try:
        file_path = Path(file_path).resolve()  # Ensure absolute path
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        logging.info(f"Loading PDF file: {file_path}")
        loader = PDFPlumberLoader(str(file_path))  # Convert Path to string
        documents = loader.load()
        logging.info(f"Successfully loaded PDF file with {len(documents)} pages")
        return documents
    except Exception as e:
        logging.error("Error in loading PDF file")
        raise CustomException(e, sys)

# Define the file path
file_path = pdfs_directory / "udhr_booklet_en_web.pdf"

# Ensure the file exists before loading
if file_path.exists():
    documents = load_pdf(file_path)
    print("PDF pages:", len(documents))
else:
    print(f"Error: File not found at {file_path}")

#Step 2: Create Chunks
def create_chunks(documents): 
    logging.info("Creating chunks for PDF document")
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 1000,
            chunk_overlap = 200,
            add_start_index = True
        )
        text_chunks = text_splitter.split_documents(documents)
        logging.info(f"Successfully covert PDF into {len(text_chunks)} chunks")
        return text_chunks
    except Exception as e:
        logging.error("Error while creating chunks")
        raise CustomException(e,sys)

text_chunks = create_chunks(documents)
print("Chunks count: ", len(text_chunks))

# Step 3: Setup Embeddings Model
ollama_model_name = "deepseek-r1:1.5b"
def get_embedding_model(model_name):
    try:
        logging.info("Creating vector embeddings")
        embeddings = OllamaEmbeddings(model=model_name)
        logging.info("Vector embeddings created successfully")
        return embeddings
    except Exception as e:
        logging.error("Error in creating vector embeddings")
        raise CustomException(e, sys)

embedding_model = get_embedding_model(ollama_model_name)

# Step 4: Store Embeddings in FAISS
try:
    logging.info("Storing embeddings in FAISS")
    DB_FAISS_PATH = Path("vectorstore/db_faiss").resolve()
    DB_FAISS_PATH.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists

    db = FAISS.from_documents(text_chunks, embedding_model)
    db.save_local(str(DB_FAISS_PATH))

    logging.info("Embeddings stored successfully in FAISS")
    print(f"Embeddings saved at: {DB_FAISS_PATH}")

except Exception as e:
    logging.error("Error in storing embeddings")
    raise CustomException(e, sys)