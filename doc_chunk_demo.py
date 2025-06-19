# === Environment Setup ===
import os
from dotenv import load_dotenv
load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")

# === Imports ===
import streamlit as st
from tempfile import NamedTemporaryFile
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI

# === 1. Load OpenAI API key ===
load_dotenv()
openai_key = os.getenv("Please write your OpenAI API key here")

# ===  Streamlit UI ===
st.set_page_config(page_title="LLM-Powered Document Q&A", layout="centered")
st.title("📄 LLM-Powered Document Q&A System")
st.markdown("Upload a PDF file and ask any question. The system will answer based on the document content.")

uploaded_file = st.file_uploader("📎 Upload your PDF document", type=["pdf"])
query = st.text_input("💬 Enter your question (English preferred)")

if uploaded_file and query:
    with st.spinner("Processing the document..."):
        # === 3. Save uploaded file temporarily  ===
        with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        # === 4. Load and split the document  ===
        loader = PyPDFLoader(tmp_path)
        documents = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        chunks = splitter.split_documents(documents)

        # === 5. Embed chunks into vectors using OpenAI  ===
        embedding = OpenAIEmbeddings(openai_api_key=openai_key)
        db = FAISS.from_documents(chunks, embedding)

        # === 6. Build a RetrievalQA chain  ===
        qa = RetrievalQA.from_chain_type(
            llm=ChatOpenAI(temperature=0, openai_api_key=openai_key),
            retriever=db.as_retriever()
        )

        result = qa.run("Please answer in English: " + query)

        # === 7. Show the result  ===
        st.success("✅ Answer generated:")
        st.markdown("**🤖 Answer:**")
        st.write(result)

