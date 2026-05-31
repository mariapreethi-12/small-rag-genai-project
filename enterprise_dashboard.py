import os

import requests
import streamlit as st


st.set_page_config(page_title="Enterprise RAG Dashboard", layout="wide")
st.title("Enterprise Multi-Agent Knowledge Assistant")
st.caption("FastAPI control panel for ingestion, Q&A, evaluation, and analytics.")

api_url = st.sidebar.text_input("API URL", value="http://localhost:8000")
api_key = st.sidebar.text_input("API key", value=os.getenv("APP_API_KEY", "dev-local-key"), type="password")
headers = {"X-API-Key": api_key}

tabs = st.tabs(["Ask", "Ingest", "Evaluate", "Analytics"])

with tabs[0]:
    question = st.text_input("Question", value="What does Acme Learning do?")
    conversation_id = st.text_input("Conversation ID", value="demo")
    top_k = st.slider("Top K", 1, 12, 5)
    if st.button("Ask", type="primary"):
        response = requests.post(
            f"{api_url}/ask",
            json={"question": question, "conversation_id": conversation_id, "top_k": top_k},
            headers=headers,
            timeout=60,
        )
        st.write(response.json())

with tabs[1]:
    paths = st.text_area("Local paths, one per line", value="data")
    urls = st.text_area("Website URLs, one per line")
    github_repos = st.text_area("GitHub repo URLs, one per line")
    if st.button("Ingest Sources", type="primary"):
        payload = {
            "paths": [line.strip() for line in paths.splitlines() if line.strip()],
            "urls": [line.strip() for line in urls.splitlines() if line.strip()],
            "github_repos": [line.strip() for line in github_repos.splitlines() if line.strip()],
        }
        response = requests.post(f"{api_url}/ingest", json=payload, headers=headers, timeout=180)
        st.write(response.json())

with tabs[2]:
    questions = st.text_area("Evaluation questions", value="What does Acme Learning do?")
    keywords = st.text_input("Expected keywords, comma-separated", value="education, knowledge")
    if st.button("Run Evaluation", type="primary"):
        payload = {
            "questions": [line.strip() for line in questions.splitlines() if line.strip()],
            "expected_keywords": [word.strip() for word in keywords.split(",") if word.strip()],
        }
        response = requests.post(f"{api_url}/evaluate", json=payload, headers=headers, timeout=180)
        st.write(response.json())

with tabs[3]:
    if st.button("Refresh Analytics"):
        response = requests.get(f"{api_url}/analytics", headers=headers, timeout=30)
        st.write(response.json())
