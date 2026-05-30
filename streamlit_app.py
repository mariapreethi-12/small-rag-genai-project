import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from app import (
    DATA_DIR,
    INDEX_PATH,
    answer_question,
    build_index,
    load_index,
    retrieve,
)


load_dotenv()

st.set_page_config(
    page_title="RAG Knowledge Assistant",
    layout="wide",
)

st.title("RAG Knowledge Assistant")
st.caption("A small GenAI app with retrieval, citations, uploadable knowledge files, and transparent source scores.")


def get_client() -> OpenAI | None:
    if not os.getenv("OPENAI_API_KEY"):
        st.error("OPENAI_API_KEY is missing. Add it to .env before running the app.")
        return None
    return OpenAI()


with st.sidebar:
    st.header("Knowledge Base")
    uploaded_files = st.file_uploader(
        "Add Markdown, text, or PDF files",
        type=["md", "txt", "pdf"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        DATA_DIR.mkdir(exist_ok=True)
        for uploaded_file in uploaded_files:
            destination = DATA_DIR / Path(uploaded_file.name).name
            destination.write_bytes(uploaded_file.getbuffer())
        st.success(f"Saved {len(uploaded_files)} file(s) to data/.")

    embedding_model = st.text_input(
        "Embedding model",
        value=os.getenv("RAG_EMBEDDING_MODEL", "text-embedding-3-small"),
    )
    chat_model = st.text_input(
        "Answer model",
        value=os.getenv("RAG_CHAT_MODEL", "gpt-4.1-mini"),
    )
    top_k = st.slider("Retrieved chunks", min_value=1, max_value=6, value=3)

    if st.button("Rebuild Index", type="primary", use_container_width=True):
        client = get_client()
        if client:
            with st.spinner("Embedding documents..."):
                records = build_index(client, embedding_model)
            st.success(f"Indexed {len(records)} chunks.")


left, right = st.columns([0.62, 0.38], gap="large")

with left:
    st.subheader("Ask a Question")
    question = st.text_input(
        "Question",
        value="What does Acme Learning do?",
        label_visibility="collapsed",
    )
    ask = st.button("Generate Answer", type="primary")

    if ask:
        client = get_client()
        if client and question.strip():
            if not INDEX_PATH.exists():
                st.warning("No index found yet. Click Rebuild Index first.")
            else:
                with st.spinner("Retrieving context and generating answer..."):
                    records = load_index()
                    contexts = retrieve(client, question, records, embedding_model, top_k)
                    answer = answer_question(client, question, contexts, chat_model)
                st.markdown("### Answer")
                st.write(answer)
                st.session_state["last_contexts"] = contexts

with right:
    st.subheader("Retrieved Evidence")
    contexts = st.session_state.get("last_contexts", [])
    if not contexts:
        st.info("Ask a question to see the chunks used by the model.")
    for item in contexts:
        with st.expander(f"{item['id']} - score {item['score']:.3f}"):
            st.write(item["chunk"])

st.divider()
st.markdown(
    """
**Recruiter highlights:** retrieval-augmented generation, document ingestion,
OpenAI embeddings, cosine similarity search, grounded answers, source citations,
and a usable Streamlit interface.
"""
)
