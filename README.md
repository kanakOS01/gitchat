# 🤖 GitChat

GitChat is an open-source application that lets you **chat with public GitHub repositories** using Large Language Models (LLMs) like OpenAI's GPT.
You can ask questions about any ingested repository, and the system will fetch relevant context from its codebase using **RAG (Retrieval-Augmented Generation)**.

---

## ✨ Features

- 🗂 **Ingest any public GitHub repo** and store its code in a vector database.
- 🔍 **Semantic search** for relevant code snippets using embeddings.
- 💬 **Chat interface** with streaming responses from LLMs.
- 📦 **Centralized vector store** for all repos (shared across users).
- 📑 **Metadata management** via MongoDB.
- 🔄 **Multi-model support** — OpenAI, Google AI (future: Anthropic, local LLMs).
- ⚡ **FastAPI backend** + **Streamlit frontend**.

---

## 🏗 Architecture Overview
```
      ┌────────────────┐
      │   Streamlit UI │
      └───────┬────────┘
              │
      ┌───────▼──────────┐
      │   FastAPI API    │
      ├────────┬─────────┤
      │ /gh    │ /chat   │
      └────────┴─────────┘
              │
  ┌───────────▼───────────────────────────┐
  │         Business Logic Layer          │
  │  - GithubManager (repo cloning, etc.) │
  │  - WeaviateManager (vector store)     │
  │  - RAGQueryEngine (context + LLM)     │
  └───────────┬───────────────────────────┘
              │
  ┌───────────▼──────────────┐
  │   MongoDB (Metadata)     │
  ├──────────────────────────┤
  │   Weaviate (Vector DB)   │
  └──────────────────────────┘
```


---

## 📂 Project Structure

```
.
├── backend
│   ├── app
│   │   ├── api
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── schemas/
│   ├── config.py
│   ├── database.py
│   ├── docker-compose.yaml
│   ├── __init__.py
│   ├── logger.py
│   ├── pyproject.toml
│   ├── utils
│   │   ├── embedder.py
│   │   ├── github_manager.py
│   │   ├── rag_engine.py
│   │   └── weaviate_manager.py
│   └── uv.lock
├── frontend
│   ├── main.py
│   ├── pages
│   │   └── chat.py
│   ├── pyproject.toml
│   ├── utils.py
│   └── uv.lock
├── logs
│   └── backend.log
├── mcp
└── README.md
```

---

## 🚀 Getting Started

### 1️⃣ Clone the repo
```bash
git clone https://github.com/yourusername/gitchat.git
cd gitchat
```

### 2️⃣ Backend Setup
1. Create a virtual environment
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

2. Setup `.env` according to `.env.example`.

3. Install the deps from `pyproject.toml`. (Or just run the code using `uv run ...` to have the deps downloaded for the first time)

4. Run the backend server
```bash
uvicorn app.main:app
```

### 3️⃣ Frontend Setup
1. Install the deps from `pyproject.toml`. (Or just run the code using `uv run ...` to have the deps downloaded for the first time)

2. Run the frontend app
```bash
cd frontend
streamlit run main.py
```



