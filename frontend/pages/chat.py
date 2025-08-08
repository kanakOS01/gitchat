import streamlit as st
from utils import stream_chat

st.set_page_config(page_title="GitChat - Chat", layout="centered")

repo = st.session_state.get("selected_repo")
if not repo:
    st.warning("Please go back to the Home page and select a repository.")
    st.stop()

# Sidebar: BYOK
st.sidebar.title("🔐 Bring Your Own Key")
st.session_state.openai_key = st.sidebar.text_input(
    "OpenAI API Key",
    type="password",
    value=st.session_state.openai_key
)

st.title(f"💬 Chatting with {repo['repo_name']}")
st.markdown(f"**Owner:** {repo['owner']}")

# Branch selection
branch_names = [b['branch'] for b in repo['branches']]
selected_branch = st.selectbox("Select branch", branch_names)

# Find the vs_collection for the selected branch
branch_data = next((b for b in repo['branches'] if b['branch'] == selected_branch), None)
if not branch_data:
    st.error("Branch data not found.")
    st.stop()

# question = st.text_input("Ask a question about this repository")
# if st.button("Ask") and question:
#     with st.spinner("Generating answer..."):
#         response_text = ""
#         placeholder = st.empty()  # Reserve a place for output
#         for chunk in stream_chat(question, branch_data['vs_collection']):
#             response_text += chunk
#             placeholder.markdown(response_text)  # Update same box, not re-add markdown
#         st.success("Done")
question = st.text_input("Ask a question about this repository")

if st.button("Ask") and question:
    with st.spinner("Generating answer..."):
        st.write_stream(stream_chat(question, branch_data['vs_collection']))  # Stream directly into the UI

    st.success("Done")
