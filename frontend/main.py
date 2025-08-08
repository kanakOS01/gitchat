import streamlit as st
from utils import fetch_repos, add_repo

st.set_page_config(page_title="GitChat - Home", layout="centered")

# Sidebar: BYOK
st.sidebar.title("🔐 Bring Your Own Key")
st.session_state.openai_key = st.sidebar.text_input(
    "OpenAI API Key",
    type="password",
    value=st.session_state.openai_key
)

st.title("🤖 GitChat")
st.markdown("Chat with public GitHub repositories using LLMs.")

st.subheader("🔍 Add a New GitHub Repo")
with st.form("add_repo_form"):
    repo_url = st.text_input("GitHub Repository URL", placeholder="https://github.com/user/repo")
    submitted = st.form_submit_button("Ingest")
    if submitted and repo_url:
        success = add_repo(repo_url)
        st.badge('Working on it! It may take a while :)')
        if success:
            st.success("Repository ingested successfully!")
        else:
            st.error("Failed to ingest repository.")

st.subheader("📂 All Available Repositories")
repos = fetch_repos()
for repo in repos:
    if st.button(f"{repo['repo_name']} by {repo['owner']}", key=repo['repo_url']):
        st.session_state.selected_repo = repo
        st.switch_page("pages/chat.py")  # Directly go to Chat page
