import os
import sys
from dotenv import load_dotenv
from src.logger import logging
from src.exception import CustomException
from langchain_groq import ChatGroq
from langchain_ollama import OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from pathlib import Path

# Load environment variables
load_dotenv()

# Step 1: Load API Key
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    logging.error("GROQ_API_KEY is not set. Please check your environment variables.")
    raise ValueError("GROQ_API_KEY is missing!")

# Step 2: Initialize LLM (DeepSeek R1 with Groq)
logging.info("Initializing DeepSeek-r1 model")
llm_model = ChatGroq(model="deepseek-r1-distill-llama-70b")

# Step 3: Load FAISS Database
logging.info("Loading FAISS database...")
try:
    DB_FAISS_PATH = Path("vectorstore/db_faiss")
    embedding_model = OllamaEmbeddings(model="deepseek-r1:1.5b")
    db = FAISS.load_local(DB_FAISS_PATH, embedding_model, allow_dangerous_deserialization=True)
    logging.info("Successfully loaded FAISS database")
except Exception as e:
    logging.error("Error in loading FAISS database")
    raise CustomException(e, sys)

# Step 4: Retrieve Documents
def retrieve_docs(query):
    """Retrieve relevant documents from the FAISS database."""
    try:
        logging.info(f"Retrieving documents for query: {query}")
        docs = db.similarity_search(query)
        if not docs:
            logging.warning("No relevant documents found.")
        return docs
    except Exception as e:
        logging.error(f"Error in retrieving documents: {str(e)}")
        raise CustomException(e, sys)

# Step 5: Generate Context from Retrieved Docs
def get_context(documents):
    """Generate context by extracting text from retrieved documents."""
    try:
        if not documents:
            return "No relevant documents found in the database."
        
        logging.info("Generating context from retrieved documents")
        context = "\n\n".join([doc.page_content for doc in documents])
        return context
    except Exception as e:
        logging.error(f"Error in generating context: {str(e)}")
        raise CustomException(e, sys)

# Step 6: Define the Custom Prompt
custom_prompt_template = """
Use the pieces of information provided in the context to answer the user's question.
If you don't know the answer, just say that you don't know; don't try to make up an answer.
Do not provide anything outside of the given context.

Question: {question} 
Context: {context} 

Answer:
"""

# Step 7: Answer the Query
def answer_query(documents, model, query):
    """Generate an answer using the LLM based on retrieved documents."""
    try:
        logging.info("Generating answer")
        context = get_context(documents)

        prompt = ChatPromptTemplate.from_template(custom_prompt_template)
        chain = prompt | model

        return chain.invoke({"question": query, "context": context})
    except Exception as e:
        logging.error(f"Error in generating answer: {str(e)}")
        raise CustomException(e, sys)

# Step 8: Example Query Execution
if __name__ == "__main__":
    question = "If a government forbids the right to assemble peacefully, which articles are violated and why?"
    retrieved_docs = retrieve_docs(question)
    answer = answer_query(documents=retrieved_docs, model=llm_model, query=question)

    print("\nAI Lawyer Answer:\n", answer)
