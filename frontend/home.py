import streamlit as st
from datetime import datetime
from utils import fetch_repos, add_repo

st.set_page_config(page_title="GitChat", layout="centered")

# Sidebar: BYOK
st.sidebar.title("🔐 Bring Your Own Key")
st.session_state.openai_key = st.sidebar.text_input(
    "OpenAI API Key",
    type="password",
    value=st.session_state.get("openai_key", "")
)

st.title("🤖 GitChat")
st.markdown("Chat with public GitHub repositories using LLMs.")

# ─────────────────────────────────────────────
# Add new repo form
# ─────────────────────────────────────────────
st.subheader("🔍 Add a New GitHub Repo")
with st.form("add_repo_form"):
    repo_url = st.text_input("GitHub Repository URL", placeholder="https://github.com/user/repo")
    submitted = st.form_submit_button("Ingest")
    if submitted and repo_url:
        st.badge('⏳ Working on it! It may take a while :)')
        success = add_repo(repo_url)
        if success:
            st.success("✅ Repository ingested successfully!")
        else:
            st.error("❌ Failed to ingest repository.")

st.divider()

# ─────────────────────────────────────────────
# Repo cards
# ─────────────────────────────────────────────
st.subheader("📂 All Available Repositories")

repos = fetch_repos()

cards_per_row = 2

for i in range(0, len(repos), cards_per_row):
    cols = st.columns(cards_per_row)
    for col, repo in zip(cols, repos[i:i + cards_per_row]):
        created_date = datetime.fromtimestamp(repo['created_at']).strftime("%Y-%m-%d")

        # Determine branch count (adjust key based on your data structure)
        branch_count = len(repo.get('branches', [])) if isinstance(repo.get('branches'), list) else repo.get('branch_count', 0)

        with col:
            st.markdown(
                f"""
                <div style="padding:1rem; border-radius:10px; 
                            margin-bottom:1rem; border: 1px solid #333; height: 100%;">
                    <h4 style="margin:0;">
                        📦 <a href="{repo['repo_url']}" target="_blank" 
                              style="color:#4EA1F3; text-decoration:none;">
                            {repo['owner']}/{repo['repo_name']}
                        </a>
                    </h4>
                    <p style="margin:0; color:gray; font-size:14px;">Last updated on {created_date}</p>
                    <p style="margin:0; color:gray; font-size:14px;">{branch_count} branches</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button("💬 Chat", key=repo['repo_url']):
                st.session_state.selected_repo = repo
                st.switch_page("pages/chat.py")
