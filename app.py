import streamlit as st

# Step 1: Upload PDF file functionality
uploaded_file = st.file_uploader("Upload PDF", type="pdf", accept_multiple_files=True)

# Step 2: Chatbot Skeleton (Question and Answers)
user_query = st.text_area("Enter your prompt: ",height=150, placeholder="Ask anything!")
ask_question = st.button("Ask AI Lawyer")

if ask_question:
    if uploaded_file:
        st.chat_message("User").write(user_query)

        # RAG pipeline
        fixed_response = "Hi,this is AI Lawyer"
        st.chat_message("AI Lawyer").write(fixed_response)

    else:
        st.error("Kindly upload valid PDF file")