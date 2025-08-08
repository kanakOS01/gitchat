import requests
import streamlit as st

API_BASE = "http://localhost:8000"

if "openai_key" not in st.session_state:
    st.session_state.openai_key = ""


def fetch_repos():
    response = requests.get(f"{API_BASE}/gh/")
    if response.status_code == 200:
        return response.json()
    return []


def add_repo(repo_url: str):
    response = requests.post(f"{API_BASE}/gh/", json={"repo_url": repo_url})
    return response.status_code == 200


def stream_chat(question: str, collection: str):
    headers = {"Authorization": f"Bearer {st.session_state.openai_key}"} if st.session_state.openai_key else {}
    with requests.post(
        f"{API_BASE}/chat/",
        json={"question": question, "collection": collection, "provider": "openai"},
        stream=True,
        headers=headers
    ) as resp:
        for chunk in resp.iter_content(chunk_size=None):
            if chunk:
                yield chunk.decode("utf-8")
