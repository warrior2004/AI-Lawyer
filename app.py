import streamlit as st
from src.rag_pipeline import answer_query, retrieve_docs, llm_model
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaEmbeddings
from src.logger import logging

load_dotenv()

# Streamlit App Configuration
st.set_page_config(page_title="AI Lawyer - RAG Chatbot", layout="wide")
st.title("📜 AI Lawyer - Legal Chatbot")


# Define FAISS Database Path
DB_FAISS_PATH = Path("vectorstore/db_faiss")

def get_vectorstore():
    """Load FAISS vector database with embeddings."""
    try:
        embedding_model = OllamaEmbeddings(model='deepseek-r1:1.5')
        db = FAISS.load_local(DB_FAISS_PATH, embedding_model, allow_dangerous_deserialization=True)
        return db
    except Exception as e:
        print(f"Error loading FAISS database: {e}")
        return None

def set_custom_prompt():
    """Define a custom prompt for the chatbot."""
    custom_prompt_template = """
    Use the pieces of information provided in the context to answer the user's question.
    If you don’t know the answer, just say that you don’t know—don’t make up an answer.
    Only provide information from the given context.

    Context: {context}
    Question: {question}

    Start your answer directly. No small talk.
    """
    return PromptTemplate(template=custom_prompt_template, input_variables=["context", "question"])

# AI Lawyer Chat Interface
st.header("💬 AI Lawyer Chat")
user_query = st.text_area("📝 Ask a legal question:", height=150, placeholder="Example: What are my rights if arrested?")

if st.button("🔍 Ask AI Lawyer"):
    if user_query.strip():
        st.chat_message("User").write(user_query)

        with st.spinner("🤖 AI Lawyer is thinking..."):
            try:
                retrieved_docs = retrieve_docs(user_query)
                
                if not retrieved_docs:
                    st.warning("⚠️ No relevant documents found. Try rephrasing your question.")
                else:
                    response = answer_query(documents=retrieved_docs, model=llm_model, query=user_query)
                    st.chat_message("AI Lawyer").write(response)
            except Exception as e:
                st.error(f"❌ Error generating response: {str(e)}")
                logging.error(f"AI Lawyer Error: {str(e)}")
    else:
        st.warning("⚠️ Please enter a question before clicking 'Ask AI Lawyer'!")
