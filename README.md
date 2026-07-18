# Competitor Intelligence Agent

A self-hosted AI agent that researches competitors, cross-references your internal product data, and generates concise sales battlecards — streamed live to the browser.

Built with [LangGraph](https://github.com/langchain-ai/langgraph), [FastAPI](https://fastapi.tiangolo.com/), and [React](https://react.dev/). Runs fully local with [Ollama](https://ollama.com/) or points to any OpenAI-compatible API.

---

## How it works

When you submit a competitor name, a multi-agent graph wakes up and runs in parallel:

```
START
 ├── Researcher      →  searches the web via Tavily
 └── Internal Analyst → queries your docs from ChromaDB
          ↓
      Strategist      →  drafts a Markdown battlecard (streamed)
          ↓
        Critic        →  reviews and either approves or sends back for revision
          ↓
         END          →  final battlecard displayed
```

Every step streams back to the UI in real time — you see research sources appear, then watch the battlecard write itself token by token.

---

## Features

- **Live streaming** — tokens stream from the LLM directly to the browser via Server-Sent Events
- **Multi-agent graph** — Researcher, Internal Analyst, Strategist, and Critic nodes run in a LangGraph state machine with automatic revision loops
- **Internal knowledge base** — upload your own PDFs, markdown files, or text docs; they get chunked and stored in ChromaDB and used during every analysis
- **Document manager** — drag-and-drop upload, view ingested docs, and delete them (removes from both disk and vector DB)
- **Research panel** — web search results and internal KB matches are shown alongside the battlecard
- **LLM-agnostic** — swap between Ollama (local) and any OpenAI-compatible provider via a single env variable
- **No cloud required** — everything runs on your machine

---

## Stack

| Layer | Technology |
|---|---|
| Agent framework | LangGraph |
| LLM / embeddings | Ollama (`llama3.1`, `nomic-embed-text`) or OpenAI-compatible |
| Web search | Tavily |
| Vector database | ChromaDB |
| Backend | FastAPI + Uvicorn |
| Frontend | React 19, Vite, React-Bootstrap |
| Package manager | [uv](https://github.com/astral-sh/uv) |

---

## Prerequisites

- Python 3.14+
- [uv](https://github.com/astral-sh/uv) — `pip install uv`
- Node.js 18+
- [Ollama](https://ollama.com/) running locally *(or an OpenAI-compatible API key)*
- A [Tavily](https://tavily.com/) API key for web search *(free tier available)*

---

## Setup

### 1. Clone

```bash
git clone https://github.com/your-username/competitor-intelligence-agent.git
cd competitor-intelligence-agent
```

### 2. Configure environment

```bash
cp .env.example .env
```

Open `.env` and fill in your values:

```env
# Use "ollama" for local models, or "openai" for any OpenAI-compatible API
LLM_MODE="ollama"
LLM_API_KEY="ollama"
LLM_BASE_URL="http://127.0.0.1:11434"

# The model used by the Strategist (main drafting agent)
LLM_MODEL="llama3.1:8b"

# The model used by the Critic (should be smarter / larger)
SMART_LLM_MODEL="llama3.1:32b"

# Get a free key at https://tavily.com
TAVILY_API_KEY="tvly-..."

# Where ChromaDB persists its data
CHROMA_DB_DIR=./data/chroma_db
```

**Using OpenAI instead of Ollama:**

```env
LLM_MODE="openai"
LLM_API_KEY="sk-..."
LLM_BASE_URL="https://api.openai.com/v1"
LLM_MODEL="gpt-4o-mini"
SMART_LLM_MODEL="gpt-4o"
```

### 3. Pull Ollama models *(skip if using OpenAI)*

```bash
ollama pull llama3.1:8b
ollama pull llama3.1:32b
ollama pull nomic-embed-text
```

### 4. Install backend dependencies

```bash
uv sync
```

### 5. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

---

## Running

You need two terminals.

**Terminal 1 — Backend:**

```bash
uv run uvicorn src.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**

```bash
cd frontend
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## Usage

### Research tab

1. Enter a competitor name (e.g. `Stripe`, `Notion`, `Salesforce`)
2. Optionally describe a focus area (`pricing and enterprise features`)
3. Click **Run Analysis**
4. Watch the research sources populate and the battlecard stream in

### Ingest tab

Upload your internal documents so the agent can compare against them:

1. Drag and drop a **PDF, Markdown, or TXT** file onto the upload area — or click to browse
2. The file is chunked and stored in ChromaDB automatically
3. All ingested documents are listed with their chunk counts
4. Click **🗑 Remove** to delete a document — this wipes it from both disk and the vector DB

Good documents to upload: product one-pagers, pricing sheets, feature comparison tables, internal wiki exports.

---

## Project structure

```
competitor-intelligence-agent/
├── src/
│   ├── agents/
│   │   ├── graph.py          # LangGraph state machine (nodes + edges)
│   │   └── state.py          # TypedDict state schema
│   ├── configs/
│   │   ├── env.py            # Environment variable loading
│   │   └── llm.py            # LLM factory (Ollama / OpenAI)
│   ├── tools/
│   │   ├── search_tool.py    # Tavily web search wrapper
│   │   └── vector_db_tool.py # ChromaDB ingest, query, delete
│   └── main.py               # FastAPI app + SSE streaming endpoint
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── ResearchForm.jsx   # Competitor input + SSE client
│       │   ├── ResearchPanel.jsx  # Web + internal source display
│       │   ├── ReportView.jsx     # Streamed markdown battlecard
│       │   └── IngestForm.jsx     # Document upload + manager
│       └── App.jsx
├── data/
│   ├── chroma_db/            # ChromaDB persistence (git-ignored)
│   └── uploads/              # Uploaded files (git-ignored)
├── .env.example
└── pyproject.toml
```

---

## API reference

The backend exposes a small REST + SSE API:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/research` | Run competitor analysis; streams SSE events |
| `POST` | `/api/ingest/upload` | Upload a document (multipart/form-data) |
| `GET` | `/api/ingest/documents` | List all ingested documents |
| `DELETE` | `/api/ingest/documents/{name}` | Remove a document from DB and disk |

Interactive docs available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) when the backend is running.

---

## Contributing

Pull requests are welcome. For significant changes, open an issue first to discuss what you'd like to change.

1. Fork the repo
2. Create a feature branch (`git checkout -b feat/my-feature`)
3. Commit your changes (`git commit -m 'feat: add my feature'`)
4. Push and open a PR

Please keep commits focused and write clear PR descriptions.

---

## License

MIT